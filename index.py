from collections import Counter
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
import re

from load import get_dates, get_index, get_parts
from utils import find_closest_preceding_number

Ref = int | str


REF_REGEX = re.compile(r"^(?P<start>\d+)(?:-(?P<end>\d+)|(?P<suffix>f{1,2})\.?)?$")


def get_num_pages(ref: Ref) -> tuple[int, int]:
    if isinstance(ref, int):
        return ref, 1
    else:
        m = REF_REGEX.match(ref)

        if not m:
            raise ValueError(f"Reference {ref} not recognized")

        m = m.groupdict()
        first_page = int(m["start"])

        if m["suffix"]:
            num_pages = len(m["suffix"]) + 1
        elif m["end"]:
            num_pages = int(m["end"]) - first_page
        else:
            num_pages = 1

        return first_page, num_pages


def get_ref_counter(vol: str, ref: Ref | dict[Ref, str], date_type: str) -> int:
    dates = get_dates(date_type)

    if isinstance(ref, dict):
        ref = list(ref.keys())[0]

    first_page, num_pages = get_num_pages(ref)

    date = dates.get(vol)

    if isinstance(date, dict):
        section = find_closest_preceding_number(date.keys(), first_page)
        date = date[section]

    return date, num_pages


def print_undated_volumes():
    dates = get_dates()

    for volume, date in dates.items():
        if date == None:
            print(volume)


def get_part_name(vol: str | int) -> str:
    parts = get_parts()
    if isinstance(vol, str):
        n_vol = int(re.search("\d+", vol).group())
    else:
        n_vol = vol

    return next(
        part["name"]
        for part in parts
        if n_vol >= part["start"] and n_vol <= part["end"]
    )


PART_COLORS = {
    "published": "#0ea5e9",  # sky-500
    "lectures": "#14b8a6",  # teal-500
    "unpublished": "#f59e0b",  # amber-500
    "notes": "#ef4444",  # red-500
}

LEGEND_LABELS = {
    "published": "Gepubliceerd (GA 1 t/m 16)",
    "lectures": "Colleges (GA 17 t/m 63)",
    "unpublished": "Ongepubliceerd (GA 64 t/m 81)",
    "notes": "Aantekeningen (GA 82 t/m 102)",
}


def plot_histogram(
    date_type: str,
    include_parts: set[str] = set(),
    include_vols: set[str | int] = set(),
    size="md",
):
    index = get_index()
    fig = plt.figure(figsize=(8, 9 if size == "lg" else 5))
    ax = fig.subplots()
    cumulative_counter = Counter()

    plotted_part_names = set()  # To avoid duplicate legend labels

    # Some statistics
    total_refs = 0
    undated_refs = 0

    for vol, refs in index.items():
        part_name = get_part_name(vol)

        if (include_parts and part_name not in include_parts) and not (
            vol and vol in include_vols
        ):
            continue

        counter = Counter()
        for ref in refs:
            year, num_pages = get_ref_counter(vol, ref, date_type)
            counter[year] += num_pages

        total_refs += len(list(counter.elements()))

        try:
            undated_refs += counter.pop(None)
        except KeyError:
            pass

        if len(counter):
            years, no_refs = zip(*counter.items())
            p = ax.bar(
                years,
                no_refs,
                bottom=[cumulative_counter[year] for year in years],
                color=PART_COLORS[part_name],
                edgecolor="white",
                label=(
                    LEGEND_LABELS[part_name]
                    if part_name not in plotted_part_names
                    else None
                ),
                width=0.8 if size == "md" else (0.6 if size == "sm" else 1),
            )

            if size == "lg":
                fontsize = "5" if len(vol) < 5 else "3.5"
            else:
                fontsize = "6" if len(vol) < 5 else "5"

            ax.bar_label(
                p,
                labels=len(years) * [vol],
                label_type="center",
                fontsize=fontsize,
            )
            cumulative_counter += counter
            plotted_part_names.add(part_name)

    print(
        f"{total_refs} references processed, {total_refs - undated_refs} dated ({100 * (total_refs - undated_refs) / total_refs:.1f}%), {undated_refs} undated"
    )

    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_minor_locator(MultipleLocator(1))

    plt.ylabel("# Pagina’s")
    plt.xlabel("Conceptiejaar" if date_type == "orig" else "Publicatiejaar")
    plt.legend()
    plt.tight_layout()
    part_postfix = "_" + "-".join(sorted(include_parts)) if include_parts else ""
    plt.savefig(f"figures/phusis-{date_type}{part_postfix}.png", dpi=500)


if __name__ == "__main__":
    plot_histogram("orig", size="lg")
    plot_histogram("pub")
    plot_histogram("orig", include_parts={"lectures"}, size="sm")
    plot_histogram("orig", include_parts={"unpublished", "notes"})
    plot_histogram("ga")
