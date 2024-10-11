import yaml
from typing import TypedDict

from utils import first_item, first_value


RefValue = str | int
Categories = list[str]

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


def apply_errata(index: IndexObj, errata: IndexObj):
    for vol, corrections in errata.items():
        for corr in corrections:
            if isinstance(corr, dict) and not isinstance(first_value(corr), list):
                old_ref, new_ref = first_item(corr)

                try:
                    ref_index, orig_ref = next(
                        (index, orig_ref)
                        for index, orig_ref in enumerate(index[vol])
                        if old_ref == orig_ref
                        or (isinstance(orig_ref, dict) and old_ref)
                    )
                except StopIteration:
                    raise ValidationError(
                        f"Error correcting volume {vol}: reference {corr} not found (make sure no categories are assigned to this ref in the original index)"
                    )

                if new_ref == None:
                    # Reference should be removed
                    index[vol].pop(ref_index)
                else:
                    # Reference should be replaced
                    if isinstance(orig_ref, dict):
                        categories = first_value(orig_ref)

                        new_ref = {new_ref: categories}

                    index[vol][ref_index] = new_ref
            else:
                # Reference should be added
                if vol not in index.keys():
                    index[vol] = []

                index[vol].append(corr)

    return index


def load_index_yaml(include_corrections=True) -> IndexObj:

    print(f"Loading {'uncorrected ' if not include_corrections else ''}index")
    with open("index/index.yml") as f:
        index = yaml.safe_load(f)

    if include_corrections:
        with open("index/errata.yml") as f:
            errata = yaml.safe_load(f)

        index = apply_errata(index, errata)

        with open("index/complement.yml") as f:
            complement = yaml.safe_load(f)

        if set(index.keys()).intersection(complement.keys()):
            raise ValueError("Complement has an overlapping volume with index")

        index = {**index, **complement}

    return index


def validate_and_clean_dates(dates) -> DatesObj:
    clean_dates = dict()

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

        clean_dates[str(volume)] = date

    return clean_dates


def load_dates_yaml(date_type: str) -> DatesObj:
    print(f"Loading {date_type} dates")
    with open(f"dates/{date_type}.yml") as f:
        dates_yml = yaml.safe_load(f)

    return validate_and_clean_dates(dates_yml)


def load_parts_yaml() -> PartsObj:
    print("Loading parts")
    with open("parts.yml") as f:
        parts = yaml.safe_load(f)

    return parts
