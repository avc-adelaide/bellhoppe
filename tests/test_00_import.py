import pytest

def test_import_arlpy():
    try:
        import bellhop.bellhop as pm
    except ImportError as e:
        pytest.exit(f"❌ Cannot import arlpy.uwapm: {e}", returncode=1)

    # sanity check: make sure bellhop is registered
    if "bellhop" not in pm.models():
        pytest.exit("❌ 'bellhop' model not available in arlpy.uwapm. This probably means that bellhop.exe is not available on the current $PATH.", returncode=1)

    # If everything is fine, the test passes
    assert True
