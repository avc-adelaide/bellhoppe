import pytest
import bellhop as bh
import numpy as np



def test_local():
    """Test with default settings to calculate arrival times. Just check that there are no execution errors.
    """

    env = bh.read_env2d("tests/MunkB_geo_rot/MunkB_geo_rot")
    ssp = bh.read_ssp("tests/MunkB_geo_rot/MunkB_geo_rot")
    print(ssp)
    print(ssp.shape)
    print(ssp.shape[0])
    print(ssp.shape[1])
    
    # Multi-profile SSP files return pandas DataFrames, not numpy arrays
    # Check if it's a DataFrame (multi-profile) or numpy array (single-profile)
    if hasattr(ssp, 'columns'):  # pandas DataFrame
        assert ssp.ndim == 2, 'soundspeed DataFrame must be 2D'
        assert len(ssp.columns) > 0, 'soundspeed DataFrame must have range columns'
        assert len(ssp.index) > 0, 'soundspeed DataFrame must have depth rows'
    else:  # numpy array (single-profile)
        assert ssp.ndim == 2, 'soundspeed must be an Nx2 array'
        assert ssp.shape[1] == 2, 'soundspeed must be an Nx2 array'

    env["soundspeed"] = ssp
    arr = bh.compute_arrivals(env,debug=True)
    print(arr)


