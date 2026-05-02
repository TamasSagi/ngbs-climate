from typing import Any

import pytest

from ngbs_api import ThermostatData
from ngbs_api.errors import (
    MissingThermostatDataFieldError,
    MissingThermostatsData,
    ThermostatKeyError,
    WrongThermostatCount,
)
from ngbs_api.models import (
    InvalidFormatError,
    InvalidIntegerError,
    OutOfRangeError,
    ThermostatID,
    ThermostatsData,
)


def test_valid_from_str():
    t = ThermostatID.from_str("3.7")

    assert t.icon_id == 3
    assert t.thermostat_id == 7


@pytest.mark.parametrize(
    "key,expected_exception",
    [
        ("37", InvalidFormatError),  # missing dot
        ("1.2.3", InvalidFormatError),  # too many parts
        ("x.y", InvalidIntegerError),  # non numeric
        ("3.x", InvalidIntegerError),  # partial integer
    ],
)
def test_invalid_formats(key: str, expected_exception: type[ThermostatKeyError]):
    with pytest.raises(expected_exception):
        ThermostatID.from_str(key)


@pytest.mark.parametrize("idx", [0, 9, -1, 100])
def test_icon_id_out_of_range(idx: int):
    with pytest.raises(OutOfRangeError):
        ThermostatID.from_str(f"{idx}.3")

    with pytest.raises(OutOfRangeError):
        ThermostatID.from_str(f"3.{idx}")


def test_roundtrip():
    original = ThermostatID(icon_id=2, thermostat_id=5)

    assert ThermostatID.from_str(str(original)) == original


#################### ThermostatsData tests ####################


@pytest.fixture
def live_thermostat() -> dict[str, Any]:
    values: dict[str, object] = {}

    for label in ThermostatData.FIELDS.values():
        if label == "LIVE":
            values[label] = 1
        elif label in {"CE", "HC"}:
            values[label] = 0
        elif label in {"PL", "DWP", "DI", "FROST"}:
            values[label] = 0
        elif label == "NAME":
            values[label] = "TEST"
        else:
            values[label] = 42

    return values


@pytest.fixture
def inactive_thermostat(live_thermostat: dict[str, Any]) -> dict:
    payload = live_thermostat.copy()
    payload["LIVE"] = 0

    return payload


@pytest.mark.parametrize("data", [{}, {"DP": {}}])
def test_wrong_dp(data: dict):
    with pytest.raises(MissingThermostatsData):
        ThermostatsData.from_response(data)


def test_wrong_thermostat_count(inactive_thermostat: dict[str, Any]):
    dp = {"1.1": inactive_thermostat}

    with pytest.raises(WrongThermostatCount):
        ThermostatsData.from_response({"DP": dp})


def test_live_filtering(live_thermostat: dict[str, Any], inactive_thermostat: dict[str, Any]):
    dp = {f"1.{k}": live_thermostat if k > 1 else inactive_thermostat for k in range(1, 9)}
    result = ThermostatsData.from_response({"DP": dp})

    assert len(result.thermostats) == 7
    assert result.thermostats[0].thermostat_id == ThermostatID.from_str("1.2")


def test_sorting_order(live_thermostat: dict[str, Any]):
    dp = {
        "2.3": live_thermostat,
        "1.8": live_thermostat,
        "1.2": live_thermostat,
        "2.1": live_thermostat,
        "1.1": live_thermostat,
        "2.2": live_thermostat,
        "1.3": live_thermostat,
        "2.4": live_thermostat,
    }

    result = ThermostatsData.from_response({"DP": dp})

    assert [str(t.thermostat_id) for t in result.thermostats] == [
        "1.1",
        "1.2",
        "1.3",
        "1.8",
        "2.1",
        "2.2",
        "2.3",
        "2.4",
    ]


def test_missing_field_wrapped_with_context(live_thermostat):
    with pytest.raises(MissingThermostatDataFieldError) as exc:
        ThermostatsData.from_response({"DP": {"1.1": {"LIVE": 1}}})

    assert "in thermostat '1.1'" in str(exc.value)
