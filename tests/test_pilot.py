import csv
import json
import numpy as np
import subprocess
import sys
from pathlib import Path

from opensubsurface.pilot import skipped_diagnostics, summarize, setup_record


def test_failed_gate_records_all_cases_without_invented_distances(tmp_path):
    manifest, models = setup_record(tmp_path)
    assert len(models) == 30 and len(manifest) == 4096
    skipped_diagnostics(tmp_path, "not computed: numerical gate")
    rows = list(csv.DictReader((tmp_path / "pair-diagnostics.csv").open()))
    assert len(rows) == 144
    assert {row["status"] for row in rows} == {"not computed: numerical gate"}
    assert all(row["distance"] == "" and row["optimal_error"] == "" for row in rows)
    assert json.loads((tmp_path / "bank-status.json").read_text())["status"] == "not run"
    summarize(tmp_path, "inconclusive", "Numerical verification failed.", None)
    status = json.loads((tmp_path / "run-status.json").read_text())
    assert status["catalog_complete"] is False and status["verification_passed"] is False
    assert "inconclusive" in (tmp_path / "REPORT.md").read_text()
    np.testing.assert_array_equal(np.load(tmp_path / "currents-a.npy"), np.full(4096, 0.001))


def test_cli_preserves_the_actual_published_stop(tmp_path):
    root = Path(__file__).resolve().parents[1]
    record = root / "experiments/ert-observability-pilot/results/2026-10-08/profile-simpeg-h0.25-e128-s0.125-amg.json"
    completed = subprocess.run([sys.executable, "-m", "opensubsurface.pilot", "record-stop",
                                "--profile-record", str(record), "--output", str(tmp_path)], capture_output=True, text=True)
    assert completed.returncode == 2
    status = json.loads((tmp_path / "run-status.json").read_text())
    assert status["scientific_status"] == "inconclusive"
    assert status["catalog_complete"] is False
    assert status["profile"]["projected_full_bank_seconds"] > 43200
    assert len(list(csv.DictReader((tmp_path / "pair-diagnostics.csv").open()))) == 144
