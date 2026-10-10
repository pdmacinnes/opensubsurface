from hashlib import sha256
import json
import subprocess


def test_review_checksums_match_published_git_bytes():
    directory = "research/boundary-error-budget-review/2026-10-09"
    registry = json.loads(subprocess.check_output(["git", "show", f":{directory}/derived-data-sha256.json"]))
    assert len(registry) == 6
    for name, expected in registry.items():
        payload = subprocess.check_output(["git", "show", f":{directory}/{name}"])
        assert sha256(payload).hexdigest() == expected, f"Published checksum mismatch: {name}"
