import pytest
from reactive_simulator import ReactiveSystem

def test_basic_reactivity():
    rs = ReactiveSystem()
    lines = [
        "var a = input",
        "var b = a + 2",
        "var c = b * 3",
        "event a = 5"
    ]
    rs.process(lines)
    assert rs.variables['a'].value == 5
    assert rs.variables['b'].value == 7
    assert rs.variables['c'].value == 21

def test_multiple_events():
    rs = ReactiveSystem()
    lines = [
        "var a = input",
        "var b = a + 1",
        "event a = 1",
        "event a = 2"
    ]
    rs.process(lines)
    assert rs.variables['a'].value == 2
    assert rs.variables['b'].value == 3
