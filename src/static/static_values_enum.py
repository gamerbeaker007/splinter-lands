from enum import Enum


class ExtendedEnum(Enum):

    @classmethod
    def list_names(cls):
        return list(map(lambda c: c.name, cls))

    @classmethod
    def list_values(cls):
        return list(map(lambda c: c.value, cls))


class Format(ExtendedEnum):
    wild = 'wild'
    modern = 'modern'
