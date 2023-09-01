import yaml

IndexObj = dict[str, list[str | int]]
DatesObj = dict[str, None | int | dict[int, None | int]]


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
DATES = None
PARTS = None


def get_index() -> IndexObj:
    global INDEX

    if INDEX == None:
        print("Loading index")
        with open("index.yml") as f:
            index = yaml.safe_load(f)

        INDEX = clean_index(index)

    return INDEX


def get_dates() -> DatesObj:
    global DATES

    if DATES == None:
        print("Loading dates")
        with open("dates.yml") as f:
            dates_yml = yaml.safe_load(f)

        validate_dates(dates_yml)
        DATES = clean_dates(dates_yml)

    return DATES


def get_parts():
    global PARTS

    if PARTS == None:
        print("Loading parts")
        with open("parts.yml") as f:
            PARTS = yaml.safe_load(f)

    return PARTS
