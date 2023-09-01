def find_closest_preceding_number(numbers, n) -> int | None:
    if not numbers:
        return

    closest_preceding_number = None

    for m in numbers:
        if m <= n and (
            closest_preceding_number == None or m > closest_preceding_number
        ):
            closest_preceding_number = m

    return closest_preceding_number
