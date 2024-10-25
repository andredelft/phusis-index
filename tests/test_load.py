import pytest
from errata import apply_errata
from consts import ValidationError
from copy import deepcopy


@pytest.fixture
def index():
    return {"6.1": [20, "23ff", {60: ["Her:123"]}]}


cases = [
    (
        # Remove first reference
        {"6.1": [{20: None}]},
        {"6.1": ["23ff", {60: ["Her:123"]}]},
    ),
    (
        # Remove second reference
        {"6.1": [{"23ff": None}]},
        {"6.1": [20, {60: ["Her:123"]}]},
    ),
    (
        # Replace first reference
        {"6.1": [{"20": "21"}]},  # Should be flexible enough to match str to int
        {"6.1": [{"21": []}, "23ff", {60: ["Her:123"]}]},
    ),
    (
        # Replace second reference
        {"6.1": [{"23ff": "24"}]},
        {"6.1": [20, {"24": []}, {60: ["Her:123"]}]},
    ),
    (
        # Replace third reference
        {"6.1": [{60: 62}]},
        {"6.1": [20, "23ff", {"62": ["Her:123"]}]},
    ),
    (
        # Add a fourth reference
        {"6.1": ["72"]},
        {"6.1": [20, "23ff", {60: ["Her:123"]}, {"72": []}]},
    ),
    (
        # Add a fourth reference with categories
        {"6.1": [{"72": ["Her:123"]}]},
        {"6.1": [20, "23ff", {60: ["Her:123"]}, {"72": ["Her:123"]}]},
    ),
]

invalid_cases = [
    # Third reference cannot be removed because it has categories
    {"6.1": [{60: None}]},
]


@pytest.mark.parametrize("errata,expected", cases)
def test_valid_errata(index, errata, expected):
    index_to_correct = deepcopy(index)
    assert apply_errata(index_to_correct, errata) == expected


@pytest.mark.parametrize("errata", invalid_cases)
def test_invalid_errata(index, errata):
    index_to_correct = deepcopy(index)
    with pytest.raises(ValidationError):
        apply_errata(index_to_correct, errata)
