from dataclasses import asdict, dataclass
from time import perf_counter
import threading
import os
import json
from pathlib import Path
import time

import numpy as np
import psutil

from .domain import CURRENT_A, electrodes


@dataclass(frozen=True)
class MeshSettings:
    cell_size: float = 0.5
    extent: float = 128.0
    electrode_cell_size: float | None = None
    linear_solver: str = "lu"
    mesh_type: str = "tree"
    grading: float = 1.5
    intermediate_cell_size: float | None = None
    intermediate_extent: float = 32.0
    central_extent: float = 12.0
    source_batch_size: int = 64
    source_ball_cell_size: float | None = None
    source_ball_radius_ratio: float = 8.
    fem_core_extent: float = 12.

    def __post_init__(self):
        sizes = [self.cell_size, self.extent]
        if self.electrode_cell_size is not None:
            sizes.append(self.electrode_cell_size)
        if self.intermediate_cell_size is not None:
            sizes.append(self.intermediate_cell_size)
        if self.source_ball_cell_size is not None:
            sizes.append(self.source_ball_cell_size)
        if not all(np.isfinite(value) and value > 0 for value in sizes):
            raise ValueError("Mesh dimensions must be positive and finite")
        if self.extent < 16 or self.linear_solver not in ("lu", "amg"):
            raise ValueError("Invalid mesh extent or linear solver")
        if self.mesh_type not in ("tree", "tensor") or not 1 < self.grading <= 2:
            raise ValueError("Invalid mesh type or grading ratio")
        if not isinstance(self.source_batch_size, int) or not 1 <= self.source_batch_size <= 64 or not 12 <= self.central_extent < self.extent:
            raise ValueError("Invalid source batch size or central-region extent")
        if not np.isfinite(self.source_ball_radius_ratio) or self.source_ball_radius_ratio < 4:
            raise ValueError("Source-ball radius ratio must be finite and at least four")
        if not np.isfinite(self.fem_core_extent) or not 4 <= self.fem_core_extent < self.extent:
            raise ValueError("Invalid finite-element core extent")
        if not np.isfinite(self.intermediate_extent) or self.intermediate_extent <= 0 or (self.intermediate_cell_size is not None and self.intermediate_extent > self.extent):
            raise ValueError("Invalid intermediate refinement extent")


def graded_axis(cell_size, extent, grading, vertical=False, central_extent=12.):
    from .domain import electrodes
    end = 0. if vertical else central_extent
    central = np.arange(-central_extent, end, cell_size)
    central = np.unique(np.r_[central, end])
    if not vertical:
        central = np.unique(np.r_[central, electrodes()[:, 0]])
    distance = central_extent
    width = cell_size
    padding = []
    while distance < extent:
        width *= grading
        distance = min(extent, distance + width)
        padding.append(distance)
    if vertical:
        return np.unique(np.r_[-np.array(padding)[::-1], central])
    return np.unique(np.r_[-np.array(padding)[::-1], central, padding])


class ResourceSample:
    def __init__(self):
        self.peak_rss_bytes = 0
        self._stop = threading.Event()

    def check_limits(self):
        deadline = float(os.environ.get("OPENSUBSURFACE_DEADLINE", "inf"))
        if self.peak_rss_bytes <= 8 * 1024 ** 3 and time.time() <= deadline:
            return
        record = {"scientific_status": "inconclusive", "stop": "memory or remaining compute cap",
                  "peak_rss_bytes": self.peak_rss_bytes, "wall_seconds": perf_counter() - self.start}
        if "OPENSUBSURFACE_OUTPUT" in os.environ:
            output = Path(os.environ["OPENSUBSURFACE_OUTPUT"])
            output.mkdir(parents=True, exist_ok=True)
            (output / "resource-limit.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(record), flush=True)
        os._exit(2)

    def __enter__(self):
        process = psutil.Process()
        self.start_cpu = sum(process.cpu_times()[:2])
        self.start = perf_counter()
        def sample():
            while not self._stop.is_set():
                memory = process.memory_info()
                self.peak_rss_bytes = max(self.peak_rss_bytes, getattr(memory, "peak_wset", memory.rss))
                self.check_limits()
                self._stop.wait(0.05)
        self.thread = threading.Thread(target=sample, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exception):
        process = psutil.Process()
        memory = process.memory_info()
        self.peak_rss_bytes = max(self.peak_rss_bytes, getattr(memory, "peak_wset", memory.rss))
        self.check_limits()
        self._stop.set()
        self.thread.join()
        self.wall_seconds = perf_counter() - self.start
        self.cpu_seconds = sum(process.cpu_times()[:2]) - self.start_cpu

    def record(self):
        return {"wall_seconds": self.wall_seconds, "cpu_seconds": self.cpu_seconds,
                "peak_rss_bytes": self.peak_rss_bytes, "sampling_seconds": 0.05}


class SimpegForward:
    def __init__(self, settings, manifest):
        from discretize import TreeMesh, TensorMesh
        from pymatsolver import SolverLU, SolverCG
        from simpeg.electromagnetics.static import resistivity as dc

        locations = electrodes()
        width = 2 * settings.extent
        source_h = settings.electrode_cell_size or settings.cell_size
        finest = min(settings.cell_size, source_h, settings.source_ball_cell_size or settings.cell_size)
        count = int(round(width / finest))
        if settings.mesh_type == "tree" and (count & (count - 1) or not np.isclose(count * finest, width, atol=1e-10, rtol=0)):
            raise ValueError("Octree dimensions require a power-of-two cell count")
        ratios = (settings.cell_size / finest, source_h / finest)
        if settings.mesh_type == "tree" and any(not np.isclose(np.log2(ratio), round(np.log2(ratio)), atol=1e-12, rtol=0) for ratio in ratios):
            raise ValueError("Octree resolution ratios must be powers of two")
        if source_h > settings.cell_size:
            raise ValueError("Electrode resolution cannot be coarser than the body region")
        if settings.mesh_type == "tensor":
            xy = graded_axis(settings.cell_size, settings.extent, settings.grading, central_extent=settings.central_extent)
            z = graded_axis(settings.cell_size, settings.extent, settings.grading, vertical=True, central_extent=settings.central_extent)
            mesh = TensorMesh([np.diff(xy), np.diff(xy), np.diff(z)], origin=[xy[0], xy[0], z[0]])
        else:
            mesh = TreeMesh([[(finest, count)]] * 3, x0="CCN", diagonal_balance=True)
            mesh.refine_points(locations, padding_cells_by_level=[2, 2, 2], finalize=False)
            target_level = mesh.max_level - int(round(np.log2(settings.cell_size / finest)))
            mesh.refine_box([[-6., -6., -10.]], [[6., 6., -1.]], [target_level], finalize=False)
            if settings.electrode_cell_size is not None:
                source_level = mesh.max_level - int(round(np.log2(source_h / finest)))
                mesh.refine_box([[-12., -12., -2.]], [[12., 12., 0.]], [source_level], finalize=False)
            if settings.intermediate_cell_size is not None:
                ratio = settings.intermediate_cell_size / finest
                if ratio < 1 or not np.isclose(np.log2(ratio), round(np.log2(ratio))):
                    raise ValueError("Intermediate octree cell size requires a power-of-two ratio")
                level = mesh.max_level - int(round(np.log2(ratio)))
                radius = settings.intermediate_extent
                mesh.refine_box([[-radius, -radius, -2 * radius]], [[radius, radius, 0.]], [level], finalize=False)
            if settings.source_ball_cell_size is not None:
                local_h = settings.source_ball_cell_size
                while local_h <= max(.5, settings.cell_size):
                    level = mesh.max_level - int(round(np.log2(local_h / finest)))
                    mesh.refine_ball(locations, np.full(64, settings.source_ball_radius_ratio * local_h), np.full(64, level), finalize=False)
                    local_h *= 2
            mesh.finalize()
        receiver = dc.receivers.Pole(locations, data_type="volt")
        sources = [dc.sources.Pole([receiver], location=point, current=1.0) for point in locations]
        solver = SolverLU if settings.linear_solver == "lu" else SolverCG
        self.simulation = dc.Simulation3DNodal(mesh, survey=dc.Survey(sources), solver=solver)
        self.mesh = mesh
        self.manifest = manifest
        self.settings = settings
        self.metadata = {"solver": "simpeg", "linear_solver": settings.linear_solver,
                         "mesh": asdict(settings), "cells": mesh.n_cells, "nodes": mesh.n_nodes,
                         "boundary": "flat surface with Robin outer boundary", "source_count": 64}

    def solve(self, model=None):
        from simpeg.electromagnetics.static import resistivity as dc
        rho = 100.0 if model is None else model.background
        sigma = np.full(self.mesh.n_cells, 1 / rho)
        inside = np.zeros(self.mesh.n_cells, dtype=bool) if model is None else model.contains(self.mesh.cell_centers)
        if model is not None:
            sigma[inside] /= model.contrast
        self.simulation.sigma = sigma
        with ResourceSample() as resources:
            if self.settings.linear_solver == "amg":
                import pyamg
                self.simulation.solver_opts = {}
                matrix = self.simulation.getA().tocsr()
                np.random.seed(20261008)
                hierarchy = pyamg.smoothed_aggregation_solver(matrix, symmetry="symmetric")
                self.simulation.solver_opts = {"M": hierarchy.aspreconditioner(), "rtol": 1e-10,
                                               "atol": 0., "maxiter": 2000, "check_accuracy": True,
                                               "check_rtol": 1e-8}
            potential = np.empty((64, 64))
            self.source_injection_sums = np.empty(64)
            relative_residual = 0.
            batch_size = self.settings.source_batch_size
            for start in range(0, 64, batch_size):
                stop = min(64, start + batch_size)
                if batch_size == 64:
                    simulation = self.simulation
                else:
                    # A fresh instance avoids SimPEG's cached RHS when a survey changes.
                    survey = dc.Survey(self.simulation.survey.source_list[start:stop])
                    simulation = dc.Simulation3DNodal(self.mesh, survey=survey, sigma=sigma,
                        solver=self.simulation.solver, solver_opts=self.simulation.solver_opts)
                fields = simulation.fields()
                rhs = simulation.getRHS()
                solution = fields[:, simulation._solutionType]
                residual = simulation.getA() @ solution - rhs
                relative_residual = max(relative_residual, float(np.max(np.linalg.norm(residual, axis=0) / np.linalg.norm(rhs, axis=0))))
                if relative_residual > 1e-8:
                    raise RuntimeError(f"Linear equation residual {relative_residual:g} exceeds 1e-8")
                potential[start:stop] = simulation.dpred(f=fields).reshape(stop - start, 64)
                self.source_injection_sums[start:stop] = rhs.sum(axis=0)
                if batch_size != 64:
                    print(json.dumps({"source_batch_completed": stop, "total_sources": 64}), flush=True)
                del fields, rhs, solution, residual, simulation
            self.pole_potential_v_per_a = potential.copy()
            a, b, m, n = self.manifest.T
            voltage = CURRENT_A * (potential[a, m] - potential[b, m] - potential[a, n] + potential[b, n])
        record = {**self.metadata, **resources.record(), "maximum_relative_equation_residual": relative_residual,
                  "voxel_inclusion_volume_m3": float(self.mesh.cell_volumes[inside].sum()),
                  "representation": "cell-center inclusion assignment", "observations": len(voltage)}
        if not np.all(np.isfinite(voltage)):
            raise RuntimeError("SimPEG returned nonfinite voltages")
        return voltage, record

    def audit(self):
        locations = electrodes()
        interpolation = self.mesh.get_interpolation_matrix(locations, "N")
        coordinate_error = np.max(np.abs(interpolation @ self.mesh.nodes - locations))
        injection_error = np.max(np.abs(self.source_injection_sums - 1.))
        pole = self.pole_potential_v_per_a
        return {"maximum_coordinate_interpolation_error_m": float(coordinate_error),
                "maximum_unit_source_injection_error_a": float(injection_error),
                "maximum_reciprocity_error_v_at_1ma": float(CURRENT_A * np.max(np.abs(pole - pole.T))),
                "robin_reference_point_xy_m": np.median(self.mesh.nodes, axis=0)[:2].tolist()}

    def audit_dipoles(self):
        from simpeg.electromagnetics.static import resistivity as dc
        locations = electrodes()
        indices = np.linspace(0, len(self.manifest) - 1, 8, dtype=int)
        selected = self.manifest[indices]
        expected = []
        sources = []
        pole = self.pole_potential_v_per_a
        for a, b, m, n in selected:
            receiver = dc.receivers.Dipole(locations[m:m+1], locations[n:n+1])
            sources.append(dc.sources.Dipole([receiver], location_a=locations[a], location_b=locations[b], current=CURRENT_A))
            expected.append(CURRENT_A * (pole[a, m] - pole[b, m] - pole[a, n] + pole[b, n]))
        direct = dc.Simulation3DNodal(self.mesh, survey=dc.Survey(sources),
                                      sigma=self.simulation.sigma, solver=self.simulation.solver,
                                      solver_opts=self.simulation.solver_opts)
        with ResourceSample() as resources:
            fields = direct.fields()
            actual = direct.dpred(f=fields)
        return {"manifest_indices": indices.tolist(), "direct_voltage_v": actual.tolist(),
                "superposed_voltage_v": expected,
                "maximum_difference_v": float(np.max(np.abs(actual - expected))),
                "resources": resources.record()}


class PygimliForward:
    def __init__(self, settings, manifest):
        import pygimli as pg

        h = settings.cell_size
        xy = graded_axis(h, settings.extent, settings.grading, central_extent=settings.fem_core_extent)
        z = graded_axis(h, settings.extent, settings.grading, vertical=True)
        mesh = pg.createGrid(x=xy, y=xy, z=z)
        self.attach_mesh(mesh, settings, manifest)

    def attach_mesh(self, mesh, settings, manifest):
        import pygimli as pg
        mesh.createNeighborInfos()
        for boundary in mesh.boundaries():
            if boundary.outside():
                boundary.setMarker(-1 if abs(boundary.center().z()) < 1e-10 else -2)
        self.mesh = mesh
        self.centers = np.array([list(cell.center()) for cell in mesh.cells()])
        self.volumes = np.array([cell.size() for cell in mesh.cells()])
        scheme = pg.DataContainerERT()
        for location in electrodes():
            scheme.createSensor(location)
        scheme.resize(len(manifest))
        for name, values in zip(("a", "b", "m", "n"), manifest.T):
            scheme[name] = values
        scheme["valid"] = np.ones(len(manifest))
        self.scheme = scheme
        self.metadata = {"solver": "pygimli", "mesh": asdict(settings), "cells": mesh.cellCount(),
                         "nodes": mesh.nodeCount(), "boundary": "surface Neumann (-1), outer mixed (-2)",
                         "source_count": 64, "singularity_removal": True}

    def solve(self, model=None):
        from pygimli.physics import ert
        rho = 100.0 if model is None else model.background
        resistivity = np.full(self.mesh.cellCount(), rho)
        inside = np.zeros(len(resistivity), dtype=bool) if model is None else (
            self.region_inside if hasattr(self, "region_inside") else model.contains(self.centers))
        if model is not None:
            resistivity[inside] *= model.contrast
        with ResourceSample() as resources:
            result = ert.simulate(self.mesh, self.scheme, resistivity, calcOnly=True, sr=True, current=CURRENT_A, verbose=False)
            voltage = np.array(result["u"])
        if not np.all(np.isfinite(voltage)):
            raise RuntimeError("pyGIMLi returned nonfinite voltages")
        return voltage, {**self.metadata, **resources.record(), "voxel_inclusion_volume_m3": float(self.volumes[inside].sum()),
                         "representation": "cell-center inclusion assignment", "observations": len(voltage)}


class PygimliConformingForward(PygimliForward):
    def __init__(self, settings, manifest, model, segments=24, rings=12, target_volume=.05):
        if any(not isinstance(value, int) or value < 4 for value in (segments, rings)) or not np.isfinite(target_volume) or target_volume <= 0:
            raise ValueError("Invalid sphere facets or tetrahedron volume")
        import pygimli.meshtools as mt
        import pygimli as pg
        import tetgen
        from scipy.spatial import Delaunay
        extent = settings.extent
        world = mt.createWorld(start=[-extent, -extent, -extent], end=[extent, extent, 0.],
                               marker=1, area=1000., worldMarker=True)
        for center in model.centers:
            sphere = mt.createSphere(size=[2 * model.radius] * 3, pos=center,
                                      nSegments=segments, nRings=rings, marker=2, area=target_volume)
            world += sphere
        for location in electrodes():
            world.createNode(location, marker=-99)
        # pyGIMLi's filename bridge targets an older TetGen API; use current arrays.
        triangular = mt.refineQuad2Tri(world)
        points = np.array([list(node.pos()) for node in triangular.nodes()])
        faces = np.array([[node.id() for node in boundary.nodes()] for boundary in triangular.boundaries()], dtype=np.int32)
        markers = np.array([boundary.marker() for boundary in triangular.boundaries()], dtype=np.int32)
        # Boundary electrodes must participate in the top facets, not form T-junctions.
        top_faces = np.all(np.abs(points[faces, 2]) < 1e-12, axis=1)
        top_nodes = np.flatnonzero(np.abs(points[:, 2]) < 1e-12)
        top_triangles = top_nodes[Delaunay(points[top_nodes, :2]).simplices]
        faces = np.vstack((faces[~top_faces], top_triangles)).astype(np.int32)
        markers = np.r_[markers[~top_faces], np.full(len(top_triangles), -1, dtype=np.int32)]
        tetrahedra = tetgen.TetGen(points, faces, markers)
        tetrahedra.add_region(1, [0., 0., -extent / 2], 1000.)
        for index, center in enumerate(model.centers, 2):
            tetrahedra.add_region(index, center, target_volume)
        tetrahedra.tetrahedralize(switches="pzAaq1.2Qf")
        mesh = pg.Mesh(dim=3)
        mesh.createNodes(tetrahedra.node)
        mesh.createCells(tetrahedra.elem, tetrahedra.attributes.ravel().astype(int))
        mesh.createBoundaries(tetrahedra.trifaces, tetrahedra.triface_markers)
        self.attach_mesh(mesh, settings, manifest)
        self.region_inside = np.array(mesh.cellMarkers()) > 1
        self.geometry_id = model.identifier
        self.metadata.update({"geometry_representation": "conforming faceted sphere regions",
                              "segments": segments, "rings": rings, "target_tetrahedron_volume_m3": target_volume,
                              "mesh_generator": "TetGen array API with pyGIMLi geometry and PDE solver"})

    def solve(self, model=None):
        if model is not None and model.identifier != self.geometry_id:
            raise ValueError("A fitted mesh can only evaluate its specified geometry")
        voltage, record = super().solve(model)
        record["representation"] = "conforming faceted sphere regions"
        return voltage, record
