import pytest
import bellhop as bh


def test_settings():
    """Test settings."""

    env1 = bh.create_env()
    env2 = bh.create_env(beam_angle_min=-45,frequency=100)

    env1.check()
    env2.check()

    for s in ["frequency","beam_angle_min"]:
        assert env1[s] is not None, f"Setting should be set ({s})"
        assert env1[s] != env2[s], f"Default setting should not equal manual setting ({s})"


def test_syntax():

    env = bh.create_env()
    env.frequency = 555
    assert env['frequency'] == 555, "Settings should just work"

    env['frequency'] = 666
    assert env.frequency == 666, "Settings should just work"

def test_errors():

    env = bh.create_env()
    with pytest.raises(KeyError, match="Unknown environment configuration parameter: 'quefrency'"):
        env.quefrency = 500

    env = bh.create_env()
    with pytest.raises(ValueError, match="Invalid value for 'soundspeed_interp'"):
        env.soundspeed_interp = "plines"
