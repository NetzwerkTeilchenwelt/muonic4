import pytest
from ..lib.common.DataRecord import DataRecord


def test_init():
    d = DataRecord("Foobar")
    assert d.msg == "Foobar"
    assert str(d) == "Foobar"
