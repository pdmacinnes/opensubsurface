from dataclasses import asdict, dataclass
from time import perf_counter
import threading
import os
import json
from pathlib import Path

import numpy as np
import psutil

from .domain import CURRENT_A, electrodes


@dataclass(frozen=True)
class MeshSettings:
    cell_size: float = 0.5
    extent: float = 128.0
    electrode_cell_size: float | None = None
    linear_solver: str = "lu"

    def __post_init__(self):
        sizes = [self.cell_size, self.extent]
        if self.electrode_cell_size is not None:
            sizes.append(self.electrode_cell_size)
        if not all(np.isfinite(value) and value > 0 for value in sizes):
            raise ValueError("Mesh dimensions must be positive and finite")
        if self.extent < 16 or self.linear_solver not in ("lu", "amg"):
            raise ValueError("Invalid mesh extent or linear solver")


class ResourceSample:
    def __init__(self):
        self.peak_rss_bytes = 0
        self._stop = threading.Event()

    def __enter__(self):
        process = psutil.Process()
        self.start_cpu = sum(process.cpu_times()[:2])
        self.start = perf_counter()
        def sample():
            while not self._stop.is_set():
                memory = process.memory_info()
                self.peak_rss_bytes = max(self.peak_rss_bytes, getattr(memory, "peak_wset", memory.rss))
                if self.peak_rss_bytes > 8 * 1024 ** 3:
                    record = {"scientific_status": "inconclusive", "stop": "8 GiB resource cap",
                              "peak_rss_bytes": self.peak_rss_bytes, "wall_seconds": perf_counter() - self.start}
                    if "OPENSUBSURFACE_OUTPUT" in os.environ:
                        output = Path(os.environ["OPENSUBSURFACE_OUTPUT"])
                        output.mkdir(parents=True, exist_ok=True)
                        (output / "resource-limit.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
                    print(json.dumps(record), flush=True)
                    os._exit(2)
                self._stop.wait(0.05)
        self.thread = threading.Thread(target=sample, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exception):
        process = psutil.Process()
        memory = process.memory_info()
        self.peak_rss_bytes = max(self.peak_rss_bytes, getattr(memory, "peak_wset", memory.rss))
        self._stop.set()
        self.thread.join()
        self.wall_seconds = perf_counter() - self.start
        self.cpu_seconds = sum(process.cpu_times()[:2]) - self.start_cpu

    def record(self):
        return {"wall_seconds": self.wall_seconds, "cpu_seconds": self.cpu_seconds,
                "peak_rss_bytes": self.peak_rss_bytes, "sampling_seconds": 0.05}


class SimpegForward:
    def __init__(self, settings, manifest):
        from discretize import TreeMesh
        from pymatsolver import SolverLU, SolverCG
        from simpeg.electromagnetics.static import resistivity as dc

        locations = electrodes()
        width = 2 * settings.extent
        source_h = settings.electrode_cell_size or settings.cell_size
        finest = min(settings.cell_size, source_h)
        count = int(round(width / finest))
        if count & (count - 1) or not np.isclose(count * finest, width, atol=1e-10, rtol=0):
            raise ValueError("Octree dimensions require a power-of-two cell count")
        ratios = (settings.cell_size / finest, source_h / finest)
        if any(not np.isclose(np.log2(ratio), round(np.log2(ratio)), atol=1e-12, rtol=0) for ratio in ratios):
            raise ValueError("Octree resolution ratios must be powers of two")
        if source_h > settings.cell_size:
            raise ValueError("Electrode resolution cannot be coarser than the body region")
        mesh = TreeMesh([[(finest, count)]] * 3, x0="CCN", diagonal_balance=True)
        mesh.refine_points(locations, padding_cells_by_level=[2, 2, 2], finalize=False)
        target_level = mesh.max_level - int(round(np.log2(settings.cell_size / finest)))
        mesh.refine_box([[-6., -6., -10.]], [[6., 6., -1.]], [target_level], finalize=False)
        if settings.electrode_cell_size is not None:
            source_level = mesh.max_level - int(round(np.log2(source_h / finest)))
            mesh.refine_box([[-12., -12., -2.]], [[12., 12., 0.]], [source_level], finalize=False)
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
            fields = self.simulation.fields()
            rhs = self.simulation.getRHS()
            solution = fields[:, self.simulation._solutionType]
            residual = self.simulation.getA() @ solution - rhs
            relative_residual = float(np.max(np.linalg.norm(residual, axis=0) / np.linalg.norm(rhs, axis=0)))
            if relative_residual > 1e-8:
                raise RuntimeError(f"Linear equation residual {relative_residual:g} exceeds 1e-8")
            potential = self.simulation.dpred(f=fields).reshape(64, 64)
            a, b, m, n = self.manifest.T
            voltage = CURRENT_A * (potential[a, m] - potential[b, m] - potential[a, n] + potential[b, n])
        record = {**self.metadata, **resources.record(), "maximum_relative_equation_residual": relative_residual,
                  "voxel_inclusion_volume_m3": float(self.mesh.cell_volumes[inside].sum()),
                  "representation": "cell-center inclusion assignment", "observations": len(voltage)}
        if not np.all(np.isfinite(voltage)):
            raise RuntimeError("SimPEG returned nonfinite voltages")
        return voltage, record


class PygimliForward:
    def __init__(self, settings, manifest):
        import pygimli as pg

        h = settings.cell_size
        central = np.unique(np.r_[np.arange(-12., 12. + h / 2, h), electrodes()[:, 0]])
        # Retain exact electrode nodes while grading the remote half-space mesh.
        padding = 12. + np.cumsum(h * 1.5 ** np.arange(1, 30))
        padding = padding[padding < settings.extent]
        xy = np.unique(np.r_[-settings.extent, -padding[::-1], central, padding, settings.extent])
        zfine = np.arange(-12., h / 2, h)
        z = np.unique(np.r_[-settings.extent, -padding[::-1], zfine])
        mesh = pg.createGrid(x=xy, y=xy, z=z)
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
        inside = np.zeros(len(resistivity), dtype=bool) if model is None else model.contains(self.centers)
        if model is not None:
            resistivity[inside] *= model.contrast
        with ResourceSample() as resources:
            result = ert.simulate(self.mesh, self.scheme, resistivity, calcOnly=True, sr=True, current=CURRENT_A, verbose=False)
            voltage = np.array(result["u"])
        if not np.all(np.isfinite(voltage)):
            raise RuntimeError("pyGIMLi returned nonfinite voltages")
        return voltage, {**self.metadata, **resources.record(), "voxel_inclusion_volume_m3": float(self.volumes[inside].sum()),
                         "representation": "cell-center inclusion assignment", "observations": len(voltage)}
