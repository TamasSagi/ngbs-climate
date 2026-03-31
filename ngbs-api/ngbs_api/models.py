from typing import Any, ClassVar, Self, Type

from pydantic import BaseModel, field_validator

from .types import CEMode, HCMode


class ThermostatData(BaseModel):
    FIELDS: ClassVar[dict[str, str]] = {
        "ce_mode": "CE",
        "child_lock": "PL",
        "condensation": "DWP",
        "contact_signal": "DI",
        "cooling_dx": "DXC",
        "cooling_eco": "ECOC",
        "cooling_setpoint": "XAC",
        "dew_point": "DEW",
        "frost": "FROST",
        "hc_mode": "HC",
        "heating_dx": "DXH",
        "heating_eco": "ECOH",
        "heating_setpoint": "XAH",
        "humidity": "RH",
        "live": "LIVE",
        "manual_adjustment": "LIM",
        "name": "NAME",
        "temperature": "TEMP",
    }

    ce_mode: CEMode
    child_lock: bool
    condensation: bool
    contact_signal: bool
    cooling_dx: float
    cooling_eco: float
    cooling_setpoint: float
    dew_point: float
    frost: bool
    hc_mode: HCMode
    heating_dx: float
    heating_eco: float
    heating_setpoint: float
    humidity: float
    icon_id: int
    live: bool
    manual_adjustment: float
    name: str
    temperature: float
    thermo_id: int

    @field_validator(
        "cooling_dx",
        "cooling_eco",
        "cooling_setpoint",
        "dew_point",
        "heating_dx",
        "heating_eco",
        "heating_setpoint",
        "humidity",
        "manual_adjustment",
        "temperature",
        mode="before",
    )
    @staticmethod
    def convert_float(value):
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value)

        raise ValueError(f"Cannot convert {type(value).__name__} to float")

    @field_validator(
        "child_lock",
        "condensation",
        "contact_signal",
        "frost",
        "live",
        mode="before",
    )
    @staticmethod
    def convert_bool(value):
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")

        raise ValueError(f"Cannot convert {type(value).__name__} to bool")

    @field_validator("hc_mode", mode="before")
    @staticmethod
    def convert_hc_mode(value):
        if isinstance(value, int):
            return HCMode.HEATING if value == 0 else HCMode.COOLING

        raise ValueError(f"Cannot convert {type(value).__name__} to HCMode")

    @field_validator("ce_mode", mode="before")
    @staticmethod
    def convert_ce_mode(value):
        if isinstance(value, int):
            return CEMode.COMFORT if value == 0 else CEMode.ECONOMY

        raise ValueError(f"Cannot convert {type(value).__name__} to CEMode")

    @classmethod
    def from_response_dict(cls: Type[Self], data: dict[str, Any], icon_id: int, thermo_id: int) -> Self:
        return cls(
            icon_id=icon_id,
            thermo_id=thermo_id,
            **{field_name: data[label] for field_name, label in ThermostatData.FIELDS.items()},
        )


class GeneralData(BaseModel):
    FIELDS: ClassVar[dict[str, str]] = {
        "active": "ON",
        "ce_mode": "CE",
        "cooling_setpoint": "XAC",
        "eco_cooling": "ECOC",
        "eco_heating": "ECOH",
        "error": "ERR",
        "external_temp": "ETEMP",
        "frost_risk": "WFROST",
        "hc_mode": "HC",
        "heating_setpoint": "XAH",
        "overheat": "OVERHEAT",
        "pump_active": "PUMP",
        "water_temp": "WTEMP",
    }

    active: bool
    ce_mode: CEMode
    cooling_setpoint: float
    eco_cooling: float
    eco_heating: float
    error: bool
    external_temp: float
    frost_risk: bool
    hc_mode: HCMode
    heating_setpoint: float
    overheat: bool
    pump_active: bool
    water_temp: float

    @field_validator(
        "cooling_setpoint",
        "eco_cooling",
        "eco_heating",
        "external_temp",
        "heating_setpoint",
        "water_temp",
        mode="before",
    )
    @staticmethod
    def convert_float(value: str | int | float) -> float:
        match value:
            case str():
                return float(value)
            case int():
                return float(value)
            case float():
                return value
            case _:
                raise ValueError(f"Cannot convert {type(value).__name__} to float")

    @field_validator("active", "error", "frost_risk", "overheat", "pump_active", mode="before")
    @staticmethod
    def convert_bool(value: str | int):
        match value:
            case str():
                return value.lower() in ("true", "1", "yes", "on")
            case int():
                return bool(value)
            case _:
                raise ValueError(f"Cannot convert {type(value).__name__} to bool")

    @field_validator("hc_mode", mode="before")
    @staticmethod
    def convert_hc_mode(value: int) -> HCMode:
        if isinstance(value, int):
            return HCMode.HEATING if value == 0 else HCMode.COOLING

        raise ValueError(f"Cannot convert {type(value).__name__} to HCMode")

    @field_validator("ce_mode", mode="before")
    @staticmethod
    def convert_ce_mode(value: int) -> CEMode:
        if isinstance(value, int):
            return CEMode.COMFORT if value == 0 else CEMode.ECONOMY

        raise ValueError(f"Cannot convert {type(value).__name__} to CEMode")

    @classmethod
    def from_response_dict(cls: Type[Self], data: dict[str, Any]) -> Self:
        return cls(**{field_name: data[label] for field_name, label in GeneralData.FIELDS.items()})
