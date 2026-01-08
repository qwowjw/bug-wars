from utils.math_utils import clamp


def test_clamp_middle():
    assert clamp(5, 0, 10) == 5


def test_clamp_low():
    assert clamp(-2, 0, 10) == 0


def test_clamp_high():
    assert clamp(12, 0, 10) == 10
