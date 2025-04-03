from enum import Enum


class ExtendedEnum(Enum):

    @classmethod
    def list_names(cls):
        return list(map(lambda c: c.name, cls))

    @classmethod
    def list_values(cls):
        return list(map(lambda c: c.value, cls))


resource_list = [
    'GRAIN',
    'WOOD',
    'STONE',
    'IRON',
    'RESEARCH',
    'SPS',
]

grain_conversion_ratios = {
    'WOOD': 4,
    'STONE': 10,
    'IRON': 40,
    'RESEARCH': 200
}

production_rates = {
    'GRAIN': 0.02,
    'WOOD': 0.005,
    'STONE': 0.002,
    'IRON': 0.0005,
    'RESEARCH': 0.0001
}

consume_rates = {
    'GRAIN': 0.01,
    'WOOD': 0.005,
    'STONE': 0.002,
    'IRON': 0.0005,
}


class Format(ExtendedEnum):
    wild = 'wild'
    modern = 'modern'
