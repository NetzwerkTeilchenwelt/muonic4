import pytest
from ..analysis_scripts.check_direction import check_direction


def test_check_direction():
    f = open("test/data/check_dir_P.txt", "r")
    up, down, rate = check_direction(f)
    assert up == 153
    assert down == 48
    assert rate == 0.7611940298507462
