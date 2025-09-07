import pytest
import bellhop.bellhop as pm



def test_local():
    """Test with default settings to calculate arrival times. Just check that there are no execution errors.
    """

    env = pm.create_env2d(
        frequency=50,
        depth=51,
        tx_depth=1,
    )
    arr = pm.compute_arrivals(env,debug=True,fname_base="MunkB_geo_rot",local_env=True)
    print(arr)


