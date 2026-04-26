class MissingThermostatsData(Exception): ...


class WrongThermostatCount(Exception): ...


class ThermostatKeyError(ValueError):
    """Base class for thermostat key parsing errors."""


class InvalidFormatError(ThermostatKeyError):
    """Raised when the key is not in '<ICON_ID>.<THERMOSTAT_ID>' format."""


class InvalidIntegerError(ThermostatKeyError):
    """Raised when either part of the key is not an integer."""


class OutOfRangeError(ThermostatKeyError):
    """Raised when icon_id or thermostat_id is outside 1 - 8."""


class ThermostatParsingError(ValueError): ...


class MissingThermostatDataFieldError(ValueError):
    """Raised when the API response is missing a required field."""
