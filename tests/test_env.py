from maths.envcheck import check_imports


def test_required_imports():
    failures = [name for name, status in check_imports() if status.startswith("FAIL")]
    assert failures == [], f"missing Python sidecar packages: {failures}"
