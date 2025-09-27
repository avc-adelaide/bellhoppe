import bellhop as bh
import numpy as np
import bellhop.environment as _env

def test_negative_receiver_ranges():
    """Test that BELLHOP produces arrivals for negative receiver ranges."""

    env = bh.create_env2d(name="Test negative ranges")

    # Set up environment with negative and positive receiver ranges
    dp = env["depth"]
    env["depth"] = np.array([[-2000, dp], [2000, dp]])
    env["rx_depth"] = 10
    env["rx_range"] = np.array([-1000, -500, -1, 1, 500, 1000])

    # Verify environment is valid
    bh.check_env2d(env)

    # Verify that angle range was automatically extended for negative ranges
    assert env['beam_angle_min'] == -_env.Defaults.beam_angle_fullspace, "beam_angle_min should be automatically extended to -179 for negative ranges"
    assert env['beam_angle_max'] == +_env.Defaults.beam_angle_fullspace, "beam_angle_max should be automatically extended to 179 for negative ranges"

    # Compute arrivals
    arrivals = bh.compute_arrivals(env, debug=False, fname_base="test_negative_range")

    # Verify we have arrivals for all receiver ranges
    for i in range(len(env["rx_range"])):
        arr_subset = arrivals[arrivals.rx_range_ndx == i]
        assert len(arr_subset) > 0, f"No arrivals found for receiver range {env['rx_range'][i]}"


def test_positive_receiver_ranges_unchanged():
    """Test that positive-only receiver ranges don't trigger angle extension."""

    env = bh.create_env2d(name="Test positive ranges only")

    # Set up environment with only positive receiver ranges
    env["rx_range"] = np.array([1, 500, 1000])

    # Verify environment is valid
    bh.check_env2d(env)

    # Verify that angle range was NOT modified for positive-only ranges
    assert env['beam_angle_min'] == -_env.Defaults.beam_angle_halfspace, "beam_angle_min should not be modified for positive-only ranges"
    assert env['beam_angle_max'] == +_env.Defaults.beam_angle_halfspace, "beam_angle_max should not be modified for positive-only ranges"

    # Compute arrivals to ensure it still works
    arrivals = bh.compute_arrivals(env, debug=False, fname_base="test_positive_range")

    # Verify we have arrivals for all receiver ranges
    for i in range(len(env["rx_range"])):
        arr_subset = arrivals[arrivals.rx_range_ndx == i]
        assert len(arr_subset) > 0, f"No arrivals found for receiver range {env['rx_range'][i]}"


def test_manual_angle_override():
    """Test that manually set angles are not overridden."""

    env = bh.create_env2d(name="Test manual angle override")

    # Set up environment with negative ranges AND manual angles
    env["rx_range"] = np.array([-500, 500])
    env["beam_angle_min"] = -45  # User explicitly set narrow angle range
    env["beam_angle_max"] = 45

    # Verify environment is valid
    bh.check_env2d(env)

    # Verify that manually set angles are respected (not auto-extended)
    # The condition checks if beam_angle_min > -120, so -45 should not trigger auto-extension
    assert env['beam_angle_min'] == -45, "Manually set beam_angle_min should be preserved"
    assert env['beam_angle_max'] == 45, "Manually set beam_angle_max should be preserved"
