from typing import TypedDict

# YAML Data types

RefValue = str | int
Categories = list[str] | list[list[str]]

VolumeName = str | int
ReferenceObj = RefValue | dict[RefValue, Categories]
IndexObj = dict[VolumeName, list[ReferenceObj]]

Year = None | int
DatesObj = dict[VolumeName, Year | dict[int, Year]]


class PartObj(TypedDict):
    name: str
    start: int
    end: int


PartsObj = list[PartObj]


class ValidationError(Exception):
    pass


class DateValidationError(Exception):
    pass
