from hashlib import sha256
import json
from pathlib import Path
import shutil

import numpy as np
import pytest

from opensubsurface.p2_contact import correspondence, expected_nodes, resource_plan
from opensubsurface.p2_report import build_report, decisions


RECORD = Path("experiments/ert-p2-contact-comparison/results/2026-10-09")


def copy_record(target):
    for path in RECORD.iterdir():
        if path.suffix in (".json", ".npy", ".csv"):
            shutil.copy2(path, target / path.name)


def test_report_rejects_correspondence_with_wrong_joint_cell_coordinates(tmp_path):
    copy_record(tmp_path)
    assert build_report(tmp_path)["completed_states"] == 6
    path = tmp_path / "A-cell-centers-m.npy"
    centers = np.load(path, allow_pickle=False)
    original = centers.copy()
    other = int(np.flatnonzero((centers[:, 0] != centers[0, 0]) & (centers[:, 1] != centers[0, 1]) & (centers[:, 2] == centers[0, 2]))[0])
    centers[0, 1], centers[other, 1] = centers[other, 1], centers[0, 1]
    np.testing.assert_array_equal(np.sort(centers[:, 1]), np.sort(original[:, 1]))
    assert len(np.unique(centers, axis=0)) < len(centers)
    np.save(path, centers, allow_pickle=False)
    hashes_path = tmp_path / "raw-data-sha256.json"
    hashes = json.loads(hashes_path.read_text())
    hashes[path.name] = sha256(path.read_bytes()).hexdigest()
    hashes_path.write_text(json.dumps(hashes))
    with pytest.raises((ValueError, AssertionError)):
        build_report(tmp_path)


def test_p2_geometry_retains_cells_and_requires_explicit_materials(monkeypatch):
    import pygimli as pg
    monkeypatch.setattr("opensubsurface.p2_contact.electrodes", lambda: np.array([[-1., -1., 0.], [1., 1., 0.]]))
    axes = [np.array([-1., 0., 1.]), np.array([-1., 0., 1.]), np.array([-1., 0.])]
    linear = pg.createGrid(x=axes[0], y=axes[1], z=axes[2])
    linear.setCellAttributes([100., 1000., 100., 1000.])
    p2 = linear.createP2()
    mapping, checks = correspondence(linear, p2)
    assert checks["passed"] and checks["nodes_per_cell"] == 20
    assert sorted(mapping.tolist()) == list(range(4))
    assert p2.nodeCount() == expected_nodes(axes) == 51
    assert not np.array_equal(np.array(p2.cellAttributes()), np.array(linear.cellAttributes())[mapping])
    centers = np.array([list(cell.center()) for cell in p2.cells()])
    values = np.where(centers[:, 0] < 0, 100., 1000.)
    p2.setCellAttributes(values)
    np.testing.assert_array_equal(np.array(p2.cellAttributes()), values)
    bad = pg.createGrid(x=[-1., 0., .8], y=axes[1], z=axes[2]).createP2()
    with pytest.raises(ValueError, match="correspondence"):
        correspondence(linear, bad)


def test_resource_planning_has_both_admission_and_skip_cases():
    allowed = resource_plan(2**30, 10., 59551, 101269, 6000.)
    assert allowed["allowed"] and allowed["projected_peak_bytes"] < 8 * 2**30
    assert not resource_plan(3 * 2**30, 10., 59551, 101269, 6000.)["allowed"]
    assert not resource_plan(2**30, 10., 59551, 101269, 1.)["allowed"]


def test_diagnostic_reduction_is_separate_from_accuracy_and_missing_states():
    rows = [{"mesh": label, "state": state, "status": "completed", "passed": True}
            for label in "AC" for state in ("H", "C10", "C100")]
    ratios = [{"rms_ratio": .2, "maximum_ratio": .2} for _ in range(4)]
    extent = [{"passed": True} for _ in range(3)]
    assert decisions(rows, ratios, extent, True) == ("supported", "contact accuracy established for declared survey")
    rows[-1]["passed"] = False
    assert decisions(rows, ratios, extent, True) == ("supported", "inconclusive")
    assert decisions(rows[:-1], ratios, extent, True)[0] == "inconclusive: incomplete states"
    ratios[-1]["rms_ratio"] = .26
    assert decisions(rows, ratios, extent, True)[0] == "not supported"


def test_completed_report_matches_raw_evidence_and_refuses_changed_metrics(tmp_path):
    copy_record(tmp_path)
    summary = build_report(tmp_path)
    assert summary["native_state_solve_attempts"] == 6
    assert summary["diagnostic_hypothesis"] == "not supported"
    assert summary["contact_accuracy"] == "inconclusive"
    assert len(summary["error_ratios"]) == 4
    path = tmp_path / "p2-worker-A.json"
    record = json.loads(path.read_text())
    record["states"]["C10"]["check"]["rms"] = 0
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="differs from raw data"):
        build_report(tmp_path)


def test_failed_worker_cannot_make_a_complete_diagnostic_decision(tmp_path):
    copy_record(tmp_path)
    assert build_report(tmp_path)["diagnostic_hypothesis"] == "not supported"
    path = tmp_path / "p2-worker-C.json"
    record = json.loads(path.read_text())
    record["status"] = "failed"
    path.write_text(json.dumps(record))
    assert build_report(tmp_path)["diagnostic_hypothesis"] == "inconclusive: invalid run"
