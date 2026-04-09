from typing import Annotated

from pydantic import BeforeValidator

from ngbs_api.types import CEMode, HCMode


def try_convert_to_float(value: float | int | str) -> float:
    try:
        return float(value)

    except (TypeError, ValueError):
        raise ValueError(f"Cannot convert type {type(value).__name__} ({value}) to float")


def try_convert_to_bool(value: float | int | str) -> bool:
    match value:
        case str():
            return value.lower() in ("true", "1", "yes", "on")
        case int():
            return bool(value)
        case float():
            return bool(value)
        case _:
            raise ValueError(f"Cannot convert type {type(value).__name__} ({value}) to bool")


def try_convert_to_cemode(value: int) -> CEMode:
    if isinstance(value, int):
        return CEMode.COMFORT if value == 0 else CEMode.ECONOMY

    raise ValueError(f"Cannot convert type {type(value).__name__} ({value}) to CEMode")


def try_convert_to_hcmode(value: int) -> HCMode:
    if isinstance(value, int):
        return HCMode.HEATING if value == 0 else HCMode.COOLING

    raise ValueError(f"Cannot convert type {type(value).__name__} ({value}) to HCMode")


BoolConv = Annotated[bool, BeforeValidator(try_convert_to_bool)]
FloatConv = Annotated[float, BeforeValidator(try_convert_to_float)]
CEModeConv = Annotated[CEMode, BeforeValidator(try_convert_to_cemode)]
HCModeConv = Annotated[HCMode, BeforeValidator(try_convert_to_hcmode)]
