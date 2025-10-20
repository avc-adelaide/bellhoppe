import pytest
import bellhop as bh



def test_env():
    """Just check that there are no execution errors.
    """

    env = bh.create_env()
    print(env)
