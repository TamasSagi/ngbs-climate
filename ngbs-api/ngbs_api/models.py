from typing import Any, ClassVar, Self, Type

from pydantic import BaseModel

from ngbs_api.errors import MissingThermostatsData, WrongThermostatCount
from ngbs_api.validators import BoolConv, CEModeConv, FloatConv, HCModeConv


class ThermostatID(BaseModel):
    icon_id: int
    thermostat_id: int

    @classmethod
    def from_str(cls: Type[Self], key: str) -> Self:
        icon_id, thermostat_id = key.split(".")

        return cls(icon_id=int(icon_id), thermostat_id=int(thermostat_id))

    def __str__(self) -> str:
        return f"{self.icon_id}.{self.thermostat_id}"


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

    ce_mode: CEModeConv
    child_lock: BoolConv
    condensation: BoolConv
    contact_signal: BoolConv
    cooling_dx: FloatConv
    cooling_eco: FloatConv
    cooling_setpoint: FloatConv
    dew_point: FloatConv
    frost: BoolConv
    hc_mode: HCModeConv
    heating_dx: FloatConv
    heating_eco: FloatConv
    heating_setpoint: FloatConv
    humidity: FloatConv
    live: BoolConv
    manual_adjustment: FloatConv
    name: str
    temperature: FloatConv
    thermostat_id: ThermostatID

    @classmethod
    def from_response(cls: Type[Self], data: dict[str, Any], thermostat_id: ThermostatID) -> Self:
        return cls(
            thermostat_id=thermostat_id,
            **{field_name: data[label] for field_name, label in ThermostatData.FIELDS.items()},
        )


class ThermostatsData(BaseModel):
    thermostats: list[ThermostatData]

    @classmethod
    def from_response(cls: Type[Self], data: dict[str, Any]) -> Self:
        thermostats = []

        # Thermostat key E.G.: 1.2 (iCON id: 1, Thermostat id: 2)
        for thermostat_key, thermostat_values in data.get("DP", {}).items():
            thermostat_id = ThermostatID.from_str(thermostat_key)

            # Ignoring unused thermostats
            if not thermostat_values.get("LIVE", 0):
                continue

            thermostats.append(ThermostatData.from_response(thermostat_values, thermostat_id))

        thermostat_cnt = len(thermostats)
        if thermostat_cnt == 0:
            raise MissingThermostatsData("Thermostat data is missing from iCON response!")

        if thermostat_cnt % 8 != 0:
            raise WrongThermostatCount(f"Thermostat count '{thermostat_cnt}' is incorrect (must be a multiple of 8)!")

        # Sort by icon_id then thermostat id
        thermostats.sort(key=lambda thermostat: str(thermostat))

        return cls(thermostats=thermostats)


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

    active: BoolConv
    ce_mode: CEModeConv
    cooling_setpoint: FloatConv
    eco_cooling: FloatConv
    eco_heating: FloatConv
    error: BoolConv
    external_temp: FloatConv
    frost_risk: BoolConv
    hc_mode: HCModeConv
    heating_setpoint: FloatConv
    overheat: BoolConv
    pump_active: BoolConv
    water_temp: FloatConv

    @classmethod
    def from_response_json(cls: Type[Self], data: dict[str, Any]) -> Self:
        return cls(**{field_name: data[label] for field_name, label in GeneralData.FIELDS.items()})
