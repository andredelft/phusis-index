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


def correct_index(index, errata):
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
                    raise ValueError(
                        f"Error correcting volume {vol}: reference {ref} not found (make sure no categories are assigned to this ref in the original index)"
                    )

                if ref_value == None:
                    # Reference should be removed
                    index[vol].pop(ref_index)
                else:
                    print(vol, ref_value)
                    # Reference should be replaced
                    index[vol][ref_index] = ref_value
            else:
                # Reference should be added
                index[vol].append(ref)

    print(index)
    return index
