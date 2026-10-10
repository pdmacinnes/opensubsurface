import json
from pathlib import Path
import shutil

import numpy as np
import pytest

from opensubsurface.contact import contact_voltage, green_and_gradient, mesh_axes, prepare, verify_axes, verify_reference, worker
from opensubsurface.domain import electrodes
from opensubsurface.validation import frozen_inputs


def test_contact_literal_signed_voltage_and_both_source_sides():
    locations = np.array([[-3., 0., 0.], [3., 0., 0.], [-1., 0., 0.], [1., 0., 0.]])
    value = contact_voltage(locations, np.array([[0, 1, 2, 3]]), 100., 1000.)
    np.testing.assert_allclose(value, [11 / (80 * np.pi)], rtol=1e-12, atol=1e-14)
    assert contact_voltage(locations, np.array([[1, 0, 2, 3]]), 100., 1000.)[0] == pytest.approx(-value[0])
    source = np.array([-3., 0., 0.])
    value, gradient = green_and_gradient(np.array([[3., 0., 0.]]), source, 100., 1000.)
    assert np.all(np.isfinite(gradient))
    assert value[0] == pytest.approx(1000 / (66 * np.pi))


def test_reference_satisfies_independent_physical_identities():
    _, manifest = frozen_inputs()
    result = verify_reference(electrodes(), manifest)
    assert result["passed"]
    for values in result["identities"].values():
        assert max(values.values()) < 1e-10


@pytest.mark.parametrize("points,source,left", [
    ([[0., 0., 0.]], [0., 0., 0.], 100.),
    ([[-3., 0., 0.]], [-3., 0., 0.], 100.),
    ([[1., 0., 1.]], [-3., 0., 0.], 100.),
    ([[1., 0., 0.]], [-3., 0., -1.], 100.),
    ([[1., 0., 0.]], [-3., 0., 0.], 0.),
    ([[1., 0., 0.]], [-3., 0., 0.], float("nan")),
])
def test_reference_rejects_unsupported_or_singular_inputs(points, source, left):
    with pytest.raises(ValueError):
        green_and_gradient(points, source, left, 1000.)


def test_mesh_factors_are_nested_and_independent():
    axes = {label: mesh_axes(label) for label in "ABCD"}
    assert verify_axes(axes)["passed"]
    assert (len(axes['A'][0]), len(axes['B'][0])) == (31, 47)
    corrupted = list(axes['B'])
    corrupted[0] = corrupted[0][1:]
    axes['B'] = tuple(corrupted)
    with pytest.raises(AssertionError):
        verify_axes(axes)


def test_preparation_and_resource_stops_prevent_native_work(tmp_path):
    output = tmp_path / "study"
    prepare(output)
    with pytest.raises(ValueError, match="fresh study"):
        prepare(output)
    (output / "resource-limit.json").write_text('{}')
    with pytest.raises(RuntimeError, match="resource stop"):
        worker(output, "A")
    assert not (output / "worker-A.json").exists()
    (output / "worker-A.json").write_text('{}')
    with pytest.raises(ValueError, match="cannot be overwritten"):
        worker(output, "A")


def test_contact_published_report_recomputes_and_rejects_changed_metrics(tmp_path):
    from opensubsurface.contact_report import build_report
    directory = Path("experiments/ert-contact-benchmark/results/2026-10-09")
    for path in directory.iterdir():
        if path.suffix in (".npy", ".json", ".csv"):
            shutil.copy2(path, tmp_path / path.name)
    result = build_report(tmp_path)
    assert result["scientific_status"] == "inconclusive"
    assert result["native_state_solve_attempts"] == 12
    assert all(row["passed"] for row in result["state_errors"] if row["state"] == "H")
    assert all(not row["passed"] for row in result["state_errors"] if row["state"] != "H")
    path = tmp_path / "worker-B.json"
    record = json.loads(path.read_text())
    record["states"]["C10"]["check"]["rms"] = 0
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="differs from raw data"):
        build_report(tmp_path)
    shutil.copy2(directory / "worker-B.json", path)
    sigma_path = tmp_path / "fixed-sigma-v.npy"
    sigma = np.load(sigma_path, allow_pickle=False)
    sigma[0] += 1e-12
    np.save(sigma_path, sigma, allow_pickle=False)
    with pytest.raises(ValueError, match="checksum differs"):
        build_report(tmp_path)
