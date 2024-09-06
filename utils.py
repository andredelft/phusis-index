import re
from itertools import pairwise


def find_closest_preceding_number(sorted_numbers: list[int], n: int) -> int | None:
    sorted_numbers, n
    if sorted_numbers[0] > n:
        return None

    if sorted_numbers[-1] <= n:
        return sorted_numbers[-1]

    for n1, n2 in pairwise(sorted_numbers):
        if n1 <= n < n2:
            return n1


def volume_sort_key(volume_str: str):
    return tuple(int(n) for n in re.findall(r"\d+", volume_str))


def first_value(obj: dict):
    return next(iter(obj.values()))


def first_item(obj: dict):
    return next(iter(obj.items()))


def first_key(obj: dict):
    return next(iter(obj.keys()))
