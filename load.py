import yaml
from typing import TypedDict
from functools import cache


RefValue = str | int
Categories = str | list[str]

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


def apply_errata(index, errata):
    for vol, refs in errata.items():
        for ref in refs:
            if isinstance(ref, dict):
                ref_key, ref_value = next(iter(ref.items()))

                try:
                    ref_index = next(
                        index
                        for index, orig_ref in enumerate(index[vol])
                        if ref_key == orig_ref
                        or (
                            isinstance(orig_ref, dict)
                            and ref_key == next(iter(orig_ref.keys()))
                        )
                    )
                except StopIteration:
                    raise ValidationError(
                        f"Error correcting volume {vol}: reference {ref} not found (make sure no categories are assigned to this ref in the original index)"
                    )

                if ref_value == None:
                    # Reference should be removed
                    index[vol].pop(ref_index)
                else:
                    # Reference should be replaced
                    index[vol][ref_index] = ref_value
            else:
                # Reference should be added
                index[vol].append(ref)

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
