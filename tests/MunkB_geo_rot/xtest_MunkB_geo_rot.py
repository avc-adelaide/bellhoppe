import pytest
import bellhop as bh



def test_local():
    """Test with default settings to calculate arrival times. Just check that there are no execution errors.
    """

    env = bh.create_env2d(
        frequency=50,
        depth=51,
        tx_depth=1,
    )
    arr = bh.compute_arrivals(env,debug=True,fname_base="MunkB_geo_rot",local_env=True)
    print(arr)


