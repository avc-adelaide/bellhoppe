import pytest
import bellhop as bh
import numpy as np
import pandas as pd
import pandas.testing as pdt
import os

skip_if_coverage = pytest.mark.skipif(
    os.getenv("COVERAGE_RUN") == "true",
    reason="Skipped during coverage run"
)

env = bh.read_env2d("tests/BeamPattern/shaded.env")

def test_shaded_read_data():
    """Test using a Bellhop example that ENV file parameters are being picked up properly.
    Just check that the ATI/BTY files are read first.
    """

    assert len(env["source_directionality"]) == 37, "37 entries in SBP file"

    # bh.print_env(env)
    bh.check_env2d(env)


def test_shaded_calc():
    """Test using a Bellhop example that something is calculated.
    """

    tl = bh.compute_transmission_loss(env,mode="coherent",debug=False,fname_base="tests/BeamPattern/shaded_output")

    assert tl is not None, "No TL results calculated?"

