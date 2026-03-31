from enum import Enum


class CEMode(str, Enum):
    COMFORT = "Komfort"
    ECONOMY = "Takarékos"


class HCMode(str, Enum):
    HEATING = "Fűtés"
    COOLING = "Hűtés"
