from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
import pytest

from opensubsurface.contact import contact_voltage


FOLDER = Path("experiments/pygimli-reflection-reproduction")


@pytest.fixture
def reproduction():
    spec = importlib.util.spec_from_file_location("reflection_example", FOLDER / "reproduce.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def inputs():
    return json.loads((FOLDER / "inputs.json").read_text())


def test_changed_current_is_rejected_before_any_calculation(reproduction, inputs, tmp_path):
    inputs["current_a"] = 1.
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(inputs))
    with pytest.raises(ValueError, match="current"):
        reproduction.load_inputs(path)


@pytest.mark.parametrize("change", ["sensors", "axes", "indices", "reference", "states", "historical"])
def test_corrupt_frozen_inputs_are_rejected(reproduction, inputs, tmp_path, change):
    if change == "sensors":
        inputs["sensors_m"][0], inputs["sensors_m"][1] = inputs["sensors_m"][1], inputs["sensors_m"][0]
    elif change == "axes":
        inputs["axes_m"]["x"][0] = -129.
    elif change == "indices":
        inputs["abmn"][0][0] = 26.5
    elif change == "reference":
        inputs["references_v"]["C100"][0] = 0.
    elif change == "states":
        inputs["states_ohm_m"]["C100"][1] = 1000.
    else:
        inputs["historical_v"]["C100"][0] = 0.
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(inputs))
    with pytest.raises(ValueError):
        reproduction.load_inputs(path)


def test_inputs_match_published_record_and_independent_reference(reproduction, inputs):
    actual = reproduction.load_inputs(FOLDER / "inputs.json")
    assert actual == inputs
    sensors = np.array(inputs["sensors_m"])
    rows = np.array(inputs["abmn"])
    np.testing.assert_array_equal(sensors[rows[0]], [[-1.5,-4.5,0], [1.5,1.5,0], [7.5,1.5,0], [10.5,7.5,0]])
    np.testing.assert_array_equal(sensors[rows[1]], sensors[rows[0]] * [1,-1,1])
    root = Path(inputs["provenance"]["source_directory"])
    for axis in "xyz":
        np.testing.assert_array_equal(inputs["axes_m"][axis], np.load(root / f"C-{axis}-axis-m.npy"))
    for state, rho in inputs["states_ohm_m"].items():
        np.testing.assert_allclose(contact_voltage(sensors, rows, *rho), inputs["references_v"][state], rtol=0, atol=1e-16)
        np.testing.assert_array_equal(np.load(root / f"p2-C-{state}-voltage-v.npy")[[3646,3786]], inputs["historical_v"][state])


def test_positive_reproduction_and_explicit_non_reproduction(reproduction, inputs):
    records = {name: reproduction.measurement(values, inputs["references_v"][name], inputs["historical_v"][name])
               for name, values in inputs["historical_v"].items()}
    assert reproduction.decision(records, "completed") == "reproduced"
    wrong = deepcopy(records)
    wrong["C100"] = reproduction.measurement([-.06, -.0602], inputs["references_v"]["C100"], inputs["historical_v"]["C100"])
    assert reproduction.decision(wrong, "completed") == "not reproduced"
    assert reproduction.decision(records, "failed") == "inconclusive"
    assert reproduction.decision({"H": records["H"]}, "completed") == "inconclusive"


@pytest.mark.parametrize("values", [[float("nan"), 0.], [float("inf"), 0.], [0.]])
def test_nonfinite_or_wrong_shape_cannot_be_a_result(reproduction, inputs, values):
    with pytest.raises(ValueError, match="two finite"):
        reproduction.measurement(values, inputs["references_v"]["H"], inputs["historical_v"]["H"])


def test_failed_h_control_skips_contact_without_a_native_call(reproduction, inputs, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(reproduction, "build_mesh", lambda _: (object(), {"checked": True}))
    monkeypatch.setattr(reproduction, "environment", lambda: {"native_core_version": "test double"})
    def solve(mesh, config, state):
        calls.append(state)
        return [0., 0.]
    monkeypatch.setattr(reproduction, "solve_state", solve)
    output = tmp_path / "result.json"
    result = reproduction.run(inputs, output, {})
    assert calls == ["H"]
    assert result["states"]["C100"]["status"] == "skipped"
    assert result["decision"] == "inconclusive"
    assert json.loads(output.read_text()) == result


def test_native_exception_preserves_attempt_and_partial_output(reproduction, inputs, tmp_path, monkeypatch):
    monkeypatch.setattr(reproduction, "build_mesh", lambda _: (object(), {}))
    monkeypatch.setattr(reproduction, "environment", lambda: {})
    def fail(*args):
        raise RuntimeError("deliberate native failure")
    monkeypatch.setattr(reproduction, "solve_state", fail)
    output = tmp_path / "result.json"
    with pytest.raises(RuntimeError):
        reproduction.run(inputs, output, {})
    result = json.loads(output.read_text())
    assert result["status"] == "failed"
    assert result["state_solve_attempts"] == 1
    assert result["states"]["H"]["status"] == "attempted"
    assert result["states"]["C100"]["status"] == "skipped"
    assert result["decision"] == "inconclusive"


def test_existing_output_is_preserved_before_calculation(reproduction, inputs, tmp_path, monkeypatch):
    output = tmp_path / "result.json"
    output.write_text("existing evidence")
    monkeypatch.setattr(reproduction, "build_mesh", lambda _: pytest.fail("must not build"))
    with pytest.raises(FileExistsError):
        reproduction.run(inputs, output, {})
    assert output.read_text() == "existing evidence"


def test_validation_only_runs_outside_checkout_without_native_import(tmp_path):
    for name in ("reproduce.py", "inputs.json"):
        shutil.copy2(FOLDER / name, tmp_path / name)
    guard = """import builtins, runpy, sys
original_import = builtins.__import__
def checked_import(name, *args, **kwargs):
    if name.split('.')[0] in ('pygimli', 'pgcore', 'opensubsurface'):
        raise AssertionError('validation must not import native or project modules')
    return original_import(name, *args, **kwargs)
builtins.__import__ = checked_import
try:
    checked_import('pygimli')
except AssertionError:
    pass
else:
    raise AssertionError('import guard is ineffective')
sys.argv = ['reproduce.py', '--validate-only']
runpy.run_path('reproduce.py', run_name='__main__')
"""
    result = subprocess.run([sys.executable, "-I", "-c", guard],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "inputs valid"
    assert not (tmp_path / "results.json").exists()


def test_published_artifacts_match_git_bytes():
    registry = json.loads(subprocess.check_output(["git", "show", f":{FOLDER.as_posix()}/results/artifact-sha256.json"]))
    assert {"reproduce.py", "inputs.json", "results/results.json", "results/resources.json", "results/console.txt",
            "results/startup-failure.json", "results/startup-failure-resources.json", "results/execution-accounting.json"} <= registry.keys()
    for name, expected in registry.items():
        payload = subprocess.check_output(["git", "show", f":{FOLDER.as_posix()}/{name}"])
        assert sha256(payload).hexdigest() == expected, name
    record = json.loads(subprocess.check_output(["git", "show", f":{FOLDER.as_posix()}/results/results.json"]))
    assert record["identity"]["script_sha256"] == registry["reproduce.py"]
    assert record["identity"]["input_sha256"] == registry["inputs.json"]


def test_saved_execution_recreates_from_literal_voltages(reproduction, inputs):
    record = json.loads((FOLDER / "results/results.json").read_text())
    assert record["status"] == "completed" and record["state_solve_attempts"] == 2
    expected = {"H": [-0.0006476359420855688, -0.0006476359420855683],
                "C100": [-0.05981245281773522, -0.05995124122180487]}
    metrics = {}
    for state, values in expected.items():
        np.testing.assert_array_equal(record["states"][state]["voltage_v"], values)
        metrics[state] = reproduction.measurement(values, inputs["references_v"][state], inputs["historical_v"][state])
        for field, value in metrics[state].items():
            assert record["states"][state][field] == value
    assert reproduction.decision(metrics, "completed") == record["decision"] == "reproduced"
    resources = json.loads((FOLDER / "results/resources.json").read_text())
    assert resources["resources"]["peak_rss_bytes"] < 8 * 2**30
    assert resources["accounted_execution_seconds"] < 1800
    assert resources["outside_checkout"]
    failed = json.loads((FOLDER / "results/startup-failure.json").read_text())
    assert failed["status"] == "failed" and failed["state_solve_attempts"] == 0
    assert failed["decision"] == "inconclusive"
    ledger = json.loads((FOLDER / "results/execution-accounting.json").read_text())
    failed_resources = json.loads((FOLDER / "results/startup-failure-resources.json").read_text())
    assert ledger["native_state_solve_attempts"] == 2
    assert ledger["accounted_execution_seconds"] == resources["accounted_execution_seconds"] + failed_resources["accounted_execution_seconds"]
    assert ledger["accounted_execution_seconds"] < 1800
    assert ledger["peak_rss_bytes"] == max(resources["resources"]["peak_rss_bytes"], failed_resources["resources"]["peak_rss_bytes"])
