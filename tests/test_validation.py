from dataclasses import replace
import json
from pathlib import Path
import shutil
import numpy as np
import pytest

from opensubsurface.solvers import MeshSettings, SimpegForward, PygimliConformingForward, graded_axis
from opensubsurface.domain import electrodes, homogeneous_voltage, primary_catalog, noise_sigma, normalized_discrepancy
from opensubsurface.validation import census, frozen_inputs, start_budget, worker


def test_frozen_manifest_and_census(tmp_path):
    config, manifest = frozen_inputs()
    assert config["manifest_sha256"] == "0b04f7711ccfb05c920d43e86f5c633d065eaba7e9fb089e6f90c6eca5a62b6a"
    assert manifest.shape == (4096, 4)
    census(tmp_path)
    assert (tmp_path / "electrode-role-census.csv").read_text().count("\n") == 257


def test_graded_mesh_keeps_exact_electrodes_and_halfspace_boundary():
    axis = graded_axis(.5, 64., 1.2)
    assert axis[0] == -64 and axis[-1] == 64
    assert all(value in axis for value in (-10.5, -7.5, -4.5, -1.5, 1.5, 4.5, 7.5, 10.5))
    depth = graded_axis(.5, 64., 1.2, vertical=True)
    assert depth[0] == -64 and depth[-1] == 0
    assert np.all(np.diff(axis) > 0) and np.all(np.diff(depth) > 0)
    uneven = graded_axis(.7, 64., 1.2, vertical=True)
    assert uneven[0] == -64 and uneven[-1] == 0
    assert np.all(np.diff(uneven) > 0)


def test_batched_sources_and_direct_dipoles_preserve_voltages():
    manifest = np.array([[0, 3, 1, 2], [1, 4, 2, 5], [2, 7, 3, 6]])
    settings = MeshSettings(1., 32., linear_solver="amg")
    first = SimpegForward(settings, manifest)
    expected, _ = first.solve()
    audit = first.audit()
    assert audit["maximum_coordinate_interpolation_error_m"] == 0
    assert audit["maximum_unit_source_injection_error_a"] == 0
    assert first.audit_dipoles()["maximum_difference_v"] < 1e-10
    batched = SimpegForward(replace(settings, source_batch_size=8), manifest)
    actual, _ = batched.solve()
    np.testing.assert_allclose(actual, expected, rtol=1e-8, atol=1e-10)


def test_invalid_mesh_parameters_do_not_produce_mislabeled_results():
    with pytest.raises(ValueError):
        MeshSettings(source_batch_size=0)
    with pytest.raises(ValueError):
        MeshSettings(mesh_type="unknown")
    with pytest.raises(ValueError):
        MeshSettings(source_batch_size=1.5)


def test_fitted_geometry_keeps_electrodes_volume_and_homogeneous_reference():
    models, _ = primary_catalog()
    model = next(model for model in models.values() if model.kind == "H2" and model.depth == 3.)
    manifest = np.array([[0, 3, 1, 2], [1, 4, 2, 5], [2, 7, 3, 6]])
    forward = PygimliConformingForward(MeshSettings(extent=32.), manifest, model, 16, 8, .2)
    nodes = np.array([list(node.pos()) for node in forward.mesh.nodes()])
    assert np.max(np.min(np.linalg.norm(nodes[:, None] - electrodes()[None], axis=2), axis=0)) < 1e-12
    assert set(np.unique(forward.mesh.cellMarkers())) == {1, 2, 3}
    expected_volume = 2 * 4 * np.pi * model.radius ** 3 / 3
    assert forward.volumes[forward.region_inside].sum() == pytest.approx(expected_volume, rel=.08)
    voltage, _ = forward.solve()
    analytic = homogeneous_voltage(electrodes(), manifest)
    assert normalized_discrepancy(voltage, analytic, noise_sigma(analytic, .01, 1e-6))["passed"]
    inclusion, _ = forward.solve(model)
    assert np.max(np.abs(inclusion - voltage)) > 1e-8
    other = next(item for item in models.values() if item.identifier != model.identifier)
    with pytest.raises(ValueError, match="specified geometry"):
        forward.solve(other)


def test_published_followup_recomputes_inconclusive_evidence(tmp_path):
    from opensubsurface.validation_report import build_report
    directory = Path("experiments/ert-numerical-validation/results/2026-10-08")
    for path in directory.iterdir():
        if path.suffix in (".json", ".npy"):
            shutil.copy2(path, tmp_path / path.name)
    result = build_report(tmp_path)
    assert result["scientific_status"] == "inconclusive"
    assert len(result["unique_geometries"]) == 4
    simpeg = [row for row in result["homogeneous"] if not row["label"].startswith("independent")]
    assert len(simpeg) == 10 and all(not row["passed"] for row in simpeg)
    assert min(row["rms"] for row in simpeg) == pytest.approx(.226119, rel=1e-5)
    assert result["accounted_compute_seconds"] < 14400 and result["peak_rss_gib"] < 8
    path = tmp_path / "baseline-tree.json"
    record = json.loads(path.read_text())
    record["homogeneous_check"]["rms"] = 0
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="differs from raw data"):
        build_report(tmp_path)


def test_stopped_or_recorded_workers_cannot_reset_the_budget(tmp_path):
    (tmp_path / "resource-limit.json").write_text('{}')
    with pytest.raises(RuntimeError, match="do not continue"):
        start_budget(tmp_path)
    (tmp_path / "already-run.json").write_text('{}')
    with pytest.raises(ValueError, match="cannot be overwritten"):
        worker(tmp_path, "already-run", MeshSettings())
