from utils import first_value, first_key
from consts import IndexObj, ValidationError


def is_deletion(correction):
    """
    Checks if `correction` is a replacement and returns a parsed dictionary
    containing the reference (`str`) if it is, otherwise `None`.
    """

    if isinstance(correction, dict) and first_value(correction) == None:
        return {"reference": str(first_key(correction))}


def is_replacement(correction):
    """
    Checks if `correction` is a replacement and returns a parsed dictionary
    containing the reference (`str`) and replacement (`str`) if
    it is, otherwise `None`.
    """

    if not isinstance(correction, dict):
        return None

    value = first_value(correction)

    if isinstance(value, str) or isinstance(value, int):
        return {"reference": str(first_key(correction)), "replacement": str(value)}


def is_addition(correction):
    """
    Checks if `correction` is an addition and returns a parsed dictionary
    containing the reference (`str`) and categories (`list[str]`) if
    it is, otherwise `None`.
    """

    if not isinstance(correction, dict):
        return {"reference": str(correction), "categories": []}

    else:
        value = first_value(correction)

        # It is an addition if it has categories
        if isinstance(value, list):
            return {"reference": str(first_key(correction)), "categories": value}


def parse_correction(correction):
    if obj := is_deletion(correction):
        return "deletion", obj
    elif obj := is_replacement(correction):
        return "replacement", obj
    elif obj := is_addition(correction):
        return "addition", obj
    else:
        raise ValueError(f"{correction} could not be parsed")


def find_orig_ref(index: IndexObj, vol: str | int, ref: str):
    for index, orig_ref in enumerate(index[vol]):
        if isinstance(orig_ref, dict):
            categories = first_value(orig_ref)
            orig_ref = str(first_key(orig_ref))
        else:
            categories = []
            orig_ref = str(orig_ref)

        if orig_ref == ref:
            return index, orig_ref, categories

    raise ValueError(f"Original reference of {ref} not found")


def apply_errata(index: IndexObj, errata: IndexObj):
    for vol, corrections in errata.items():
        for corr in corrections:
            corr_type, corr_data = parse_correction(corr)

            if corr_type != "addition":
                ref_index, orig_ref, categories = find_orig_ref(
                    index, vol, corr_data["reference"]
                )

            match corr_type:
                case "deletion":
                    if categories:
                        raise ValidationError(
                            f"Reference {orig_ref} of volume {vol} cannot be deleted because it has categories"
                        )

                    index[vol].pop(ref_index)

                case "replacement":
                    index[vol][ref_index] = {corr_data["replacement"]: categories}

                case "addition":
                    if vol not in index.keys():
                        index[vol] = []

                    index[vol].append({corr_data["reference"]: corr_data["categories"]})

    return index
