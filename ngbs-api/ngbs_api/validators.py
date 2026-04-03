from typing import Annotated, Any

from pydantic import BeforeValidator

from ngbs_api import CEMode, HCMode


def try_convert_to_float(value: Any) -> float:
    try:
        return float(value)

    except (TypeError, ValueError):
        raise ValueError(f"Cannot convert {type(value).__name__} to float")


def try_convert_to_bool(value: Any):
    match value:
        case str():
            return value.lower() in ("true", "1", "yes", "on")
        case int():
            return bool(value)
        case _:
            raise ValueError(f"Cannot convert {type(value).__name__} to bool")


def try_convert_to_cemode(value: int) -> CEMode:
    if isinstance(value, int):
        return CEMode.COMFORT if value == 0 else CEMode.ECONOMY

    raise ValueError(f"Cannot convert {type(value).__name__} to CEMode")


def try_convert_to_hcmode(value: Any) -> HCMode:
    if isinstance(value, int):
        return HCMode.HEATING if value == 0 else HCMode.COOLING

    raise ValueError(f"Cannot convert {type(value).__name__} to HCMode")


BoolConv = Annotated[float, BeforeValidator(try_convert_to_bool)]
FloatConv = Annotated[float, BeforeValidator(try_convert_to_float)]
CEModeConv = Annotated[float, BeforeValidator(try_convert_to_cemode)]
HCModeConv = Annotated[float, BeforeValidator(try_convert_to_hcmode)]
