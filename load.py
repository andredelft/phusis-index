import yaml
from consts import IndexObj, DatesObj, DateValidationError, PartsObj
from errata import apply_errata


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
