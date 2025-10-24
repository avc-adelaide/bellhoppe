import pytest
import bellhop as bh
import numpy as np
import pandas as pd
import os

def test_read_biol():
    """Test reading file with biological parameters"""
    env = bh.read_env("tests/simple/biol.env")
    assert env['biological_layer_parameters'].iloc[0].z1 == 10.0, "Value expected"
    assert env['biological_layer_parameters'].iloc[1].z2 == 40.0, "Value expected"
    assert env['biological_layer_parameters'].iloc[1].Q  ==  2.5, "Value expected"
