from collections import Counter
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
import re

from load import get_dates, get_index, get_parts
from utils import find_closest_preceding_number


def get_ref_year(vol: str, ref: int | str) -> int:
    dates = get_dates()
    if isinstance(ref, str):
        page = int(re.search("\d+", ref).group())
    else:
        page = ref

    date = dates.get(vol, None)

    if isinstance(date, dict):
        section = find_closest_preceding_number(date.keys(), page)
        return date[section]

    return date


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


def plot_simple_histogram():
    index = get_index()
    parts = get_parts()
    dated_refs: dict[str, Counter] = {part["name"]: Counter() for part in parts}
    for vol, refs in index.items():
        part_name = get_part_name(vol)
        dated_refs[part_name].update(get_ref_year(vol, ref) for ref in refs)

    cumulative_counter = Counter()  # To track the bottom positions
    for part_name, counter in dated_refs.items():
        del counter[None]
        years, no_refs = zip(*counter.items())
        plt.bar(
            years,
            no_refs,
            bottom=[cumulative_counter[year] for year in years],
            label=part_name,
        )
        cumulative_counter += counter

    plt.legend()
    plt.show()


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


def plot_histogram_by_vol():
    index = get_index()
    fig, ax = plt.subplots(figsize=(12, 7))
    cumulative_counter = Counter()

    plotted_part_names = set()  # To avoid duplicate legend labels

    # Some statistics
    total_refs = 0
    undated_refs = 0

    for vol, refs in index.items():
        part_name = get_part_name(vol)
        counter = Counter(get_ref_year(vol, ref) for ref in refs)

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
                label=LEGEND_LABELS[part_name]
                if part_name not in plotted_part_names
                else None,
                width=0.8,
            )
            ax.bar_label(
                p,
                labels=len(years) * [vol],
                label_type="center",
                fontsize="6" if len(vol) < 5 else "5",
            )
            cumulative_counter += counter
            plotted_part_names.add(part_name)

    print(
        f"{total_refs} references processed, {total_refs - undated_refs} dated ({100 * (total_refs - undated_refs) / total_refs:.1f}%), {undated_refs} undated"
    )

    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_minor_locator(MultipleLocator(1))

    plt.title(
        "Het voorkomen van φύσις in Heideggers Gesamtausgabe (naar Unruhs index, 2016)"
    )
    plt.ylabel("# Referenties")
    plt.xlabel("Jaar")

    plt.legend()
    plt.savefig("unruh-phusis.png", dpi=300)
    plt.savefig(
        "/Users/andrevandelft/Documents/Filosofie/zettelkasten/_media/unruh-phusis.png",
        dpi=300,
    )
    # plt.show()


if __name__ == "__main__":
    # plot_simple_histogram()
    plot_histogram_by_vol()
