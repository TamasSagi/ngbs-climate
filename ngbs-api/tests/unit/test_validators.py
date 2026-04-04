from typing import Any

import pytest
from pydantic import TypeAdapter

from ngbs_api import CEMode, HCMode
from ngbs_api.validators import (
    FloatConv,
    try_convert_to_bool,
    try_convert_to_cemode,
    try_convert_to_float,
    try_convert_to_hcmode,
    BoolConv,
    CEModeConv,
    HCModeConv,
)


@pytest.mark.parametrize(
    "input_value,expected",
    [
        # str inputs
        ("3.14", 3.14),
        ("42", 42.0),
        ("-5.5", -5.5),
        ("0", 0.0),
        ("inf", float("inf")),
        ("-inf", float("-inf")),
        # int inputs
        (10, 10.0),
        (-42, -42.0),
        (0, 0.0),
        # float inputs
        (3.14159, 3.14159),
        (-2.5, -2.5),
        (0.0, 0.0),
        # FIXME: edge cases
        (True, 1.0),
        (False, 0.0),
    ],
)
def test_float_conversion(input_value: Any, expected: float):
    assert try_convert_to_float(input_value) == expected
    assert TypeAdapter(FloatConv).validate_python(input_value) == expected


@pytest.mark.parametrize(
    "input_value",
    [
        # invalid str inputs
        "not a number",
        "abc123",
        "",
        # invalid types
        (None,),
        [1, 2, 3],
        {"a": 1},
        (1, 2),
        object(),
    ],
)
def test_float_conversion_fail(input_value: Any):
    with pytest.raises(ValueError, match="Cannot convert type .+ to float"):
        try_convert_to_float(input_value)

    with pytest.raises(ValueError, match="Cannot convert type .+ to float"):
        TypeAdapter(FloatConv).validate_python(input_value)


@pytest.mark.parametrize(
    "input_value,expected",
    [
        # str inputs - truth values
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("1", True),
        ("yes", True),
        ("Yes", True),
        ("YES", True),
        ("on", True),
        ("On", True),
        ("ON", True),
        # str inputs - falsy values
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("0", False),
        ("no", False),
        ("off", False),
        ("", False),
        ("anything else", False),
        ("random text", False),
        # int inputs
        (1, True),
        (42, True),
        (-1, True),
        (0, False),
        # float inputs
        (1.0, True),
        (42.0, True),
        (-1.0, True),
        (0.0, False),
        (-0.0, False),
        (-123.456789, True),
    ],
)
def test_bool_conversion(input_value: Any, expected: bool):
    assert try_convert_to_bool(input_value) == expected
    assert TypeAdapter(BoolConv).validate_python(input_value) == expected


@pytest.mark.parametrize(
    "input_value",
    [
        None,
        [1, 2],
        {"a": 1},
        object(),
    ],
)
def test_bool_conversion_fail(input_value: Any):
    with pytest.raises(ValueError, match="Cannot convert type .+ to bool"):
        try_convert_to_bool(input_value)

    with pytest.raises(ValueError, match="Cannot convert type .+ to bool"):
        TypeAdapter(BoolConv).validate_python(input_value)


@pytest.mark.parametrize(
    "input_value,expected_mode",
    [
        (0, CEMode.COMFORT),
        (1, CEMode.ECONOMY),
        (2, CEMode.ECONOMY),
        (-1, CEMode.ECONOMY),
        (100, CEMode.ECONOMY),
        # FIXME: edge cases
        (False, CEMode.COMFORT),
        (True, CEMode.ECONOMY),
    ],
)
def test_cemode_conversion(input_value: int, expected_mode: CEMode):
    assert try_convert_to_cemode(input_value) == expected_mode
    assert TypeAdapter(CEModeConv).validate_python(input_value) == expected_mode


@pytest.mark.parametrize(
    "input_value",
    [
        None,
        "0",
        3.14,
        [1, 2],
        {"a": 1},
        object(),
    ],
)
def test_cemode_conversion_fail(input_value: Any):
    with pytest.raises(ValueError, match="Cannot convert type .+ to CEMode"):
        try_convert_to_cemode(input_value)

    with pytest.raises(ValueError, match="Cannot convert type .+ to CEMode"):
        TypeAdapter(CEModeConv).validate_python(input_value)


@pytest.mark.parametrize(
    "input_value,expected_mode",
    [
        (0, HCMode.HEATING),
        (1, HCMode.COOLING),
        (2, HCMode.COOLING),
        (-1, HCMode.COOLING),
        (100, HCMode.COOLING),
        # FIXME: edge cases
        (False, HCMode.HEATING),
        (True, HCMode.COOLING),
    ],
)
def test_hcmode_conversion(input_value: int, expected_mode: HCMode):
    assert try_convert_to_hcmode(input_value) == expected_mode
    assert TypeAdapter(HCModeConv).validate_python(input_value) == expected_mode


@pytest.mark.parametrize(
    "input_value",
    [
        None,
        "0",
        3.14,
        [1, 2],
        {"a": 1},
        object(),
    ],
)
def test_hcmode_conversion_fail(input_value: Any):
    with pytest.raises(ValueError, match="Cannot convert type .+ to HCMode"):
        try_convert_to_hcmode(input_value)

    with pytest.raises(ValueError, match="Cannot convert type .+ to HCMode"):
        TypeAdapter(HCModeConv).validate_python(input_value)
