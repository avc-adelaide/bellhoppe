import pytest
import bellhop as bh


def test_settings():
    """Test settings."""

    env1 = bh.create_env()
    env2 = bh.create_env(beam_angle_min=-45,frequency=100)

    env1 = bh.check_env(env1)
    env2 = bh.check_env(env2)

    for s in ["frequency","beam_angle_min"]:
        assert env1[s] is not None, f"Setting should be set ({s})"
        assert env1[s] != env2[s], f"Default setting should not equal manual setting ({s})"

