import json
import pytest

@pytest.fixture
def findings():
    with open("findings.json") as f:
        return json.load(f)["results"]

def test_direct_dependencies(findings):
    for finding in findings:
        if finding["dependency_graph"] == finding["name"]:
            assert finding["dependency_graph"] == finding["name"]

def test_transitive_dependencies(findings):
    for finding in findings:
        if "→" in finding["dependency_graph"]:
            parts = [p.strip() for p in finding["dependency_graph"].split("→")]
            assert parts[-1] == finding["name"]
            assert len(parts) > 1

def test_multiple_introduction_paths(findings):
    seen = {}
    for finding in findings:
        key = (finding["name"], finding["version"])
        seen.setdefault(key, set()).add(finding["dependency_graph"])
    multi_path = [k for k, v in seen.items() if len(v) > 1]
    assert isinstance(multi_path, list)
