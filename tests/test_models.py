import pytest
import bellhop as bh
import numpy as np

def test_models():

    env = bh.create_env()
    models = bh.models()
    print(models)
    assert models is not None

def test_models_arg():

    env = bh.create_env()
    with pytest.raises(ValueError,match="env and task should be both specified together"):
        models = bh.models(env)

def test_models_arg_task():

    env = bh.create_env()
    with pytest.raises(ValueError,match="env and task should be both specified together"):
        models = bh.models(task="foobar")

def test_models_task():

    env = bh.create_env()
    models = bh.models(env,"coherent")
    print(models)
    assert models is not None


def test_models_task():
    """I would expect this to error but it doesn't :)"""
    env = bh.create_env()
    models = bh.models(env,"foobar")
    print("foobar model?")
    print(models)
    assert models is not None
