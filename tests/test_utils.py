import pytest
from utils import category_sort_key

sort_key_cases = [("Her:123", "her:000123"), ("Aufgang", "aufgang")]


@pytest.mark.parametrize("category,expected", sort_key_cases)
def test_category_sort_key(category, expected):
    assert category_sort_key(category) == expected
