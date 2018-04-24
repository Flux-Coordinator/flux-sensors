import pytest
from .context import flux_sensors

def func(x):
    return x + 1

def test_answer():
    assert func(3) == 4