import yaml
from utils import correct_index
from typing import TypedDict


RefValue = str | int
Categories = str | list[str]

ReferenceObj = RefValue | dict[RefValue, Categories]
IndexObj = dict[str, list[ReferenceObj]]

Year = None | int
DatesObj = dict[str, Year | dict[int, Year]]


class PartObj(TypedDict):
    name: str
    start: int
    end: int


PartsObj = list[PartObj]


class ValidationError(Exception):
    pass


class DateValidationError(Exception):
    pass


def validate_dates(dates):
    for volume, date in dates.items():
        if date == None or isinstance(date, int):
            pass
        elif isinstance(date, dict):
            for page, year in date.items():
                if not isinstance(page, int):
                    raise DateValidationError(
                        f"Page {page} of volume {volume} is not of type int"
                    )
                if not (year == None or isinstance(year, int)):
                    raise DateValidationError(
                        f"Year {year} at page {page} of volume {volume} is not of type None or int"
                    )
        else:
            raise DateValidationError(
                f"Volume {volume} is not of type None, int or dict"
            )


def clean_dates(dates) -> DatesObj:
    return {str(k): v for k, v in dates.items()}


def clean_index(index) -> IndexObj:
    return {str(k): v for k, v in index.items()}


INDEX = None
DATES = dict()
PARTS = None
UNCORRECTED_INDEX = None


def get_index(include_corrections=True) -> IndexObj:
    global INDEX
    global UNCORRECTED_INDEX

    if (include_corrections and INDEX == None) or (
        not include_corrections and UNCORRECTED_INDEX == None
    ):
        print("Loading index")
        with open("index/index.yml") as f:
            index = yaml.safe_load(f)

        if include_corrections:
            with open("index/errata.yml") as f:
                errata = yaml.safe_load(f)

            index = correct_index(index, errata)

            with open("index/complement.yml") as f:
                complement = yaml.safe_load(f)

            if set(index.keys()).intersection(complement.keys()):
                raise ValueError("Complement has an overlapping volume with index")

            index = {**index, **complement}

            INDEX = clean_index(index)
        else:
            UNCORRECTED_INDEX = clean_index(index)

    return INDEX if include_corrections else UNCORRECTED_INDEX


def get_dates(date_type) -> DatesObj:
    global DATES

    if date_type not in DATES.keys():
        print("Loading dates")
        with open(f"dates/{date_type}.yml") as f:
            dates_yml = yaml.safe_load(f)

        validate_dates(dates_yml)
        DATES[date_type] = clean_dates(dates_yml)

    return DATES[date_type]


def get_parts() -> PartsObj:
    global PARTS

    if PARTS == None:
        print("Loading parts")
        with open("parts.yml") as f:
            PARTS = yaml.safe_load(f)

    return PARTS
