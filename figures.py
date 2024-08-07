from collections import Counter
from itertools import chain
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator

from index import get_index, get_dating

PART_PLOT_DATA = {
    "published": {
        "color": "#0ea5e9",  # sky-500
        "label": "Gepubliceerd (GA 1 t/m 16)",
        "short_label": "Gepubliceerd",
    },
    "lectures": {
        "color": "#14b8a6",  # teal-500
        "label": "Colleges (GA 17 t/m 63)",
        "short_label": "Colleges",
    },
    "unpublished": {
        "color": "#f59e0b",  # amber-500
        "label": "Ongepubliceerd (GA 64 t/m 81)",
        "short_label": "Ongepubliceerd",
    },
    "notes": {
        "color": "#ef4444",  # red-500
        "label": "Aantekeningen (GA 82 t/m 102)",
        "short_label": "Aantekeningen",
    },
}


def plot_histogram(
    date_type="orig",
    include_parts: list[str] = [],
    include_vols: list[str | int] = [],
    include_corrections=True,
    size="md",
):
    print(
        f"Plotting histogram with {date_type} dates",
        "without corrections" if not include_corrections else "",
    )

    index = get_index(include_corrections)
    fig = plt.figure(figsize=(8, 9 if size == "lg" else 5))
    ax = fig.subplots()
    cumulative_counter = Counter()

    plotted_part_names = set()  # Tracker to avoid duplicate legend labels

    dating = get_dating(date_type)

    if include_parts:
        parts = [index.parts[part] for part in include_parts]

        extra_vols = [
            index[vol_name]
            for vol_name in include_vols
            if index[vol_name].part_name not in include_parts
        ]
        volumes = sorted(chain(*parts, extra_vols))
    else:
        volumes = index.volumes

    for vol in volumes:
        counter = Counter()
        for ref in vol:
            year = dating.get_year(vol, ref)
            if year:
                counter[year] += len(ref)

        if len(counter):
            years, no_refs = zip(*counter.items())
            p = ax.bar(
                years,
                no_refs,
                bottom=[cumulative_counter[year] for year in years],
                color=PART_PLOT_DATA[vol.part_name]["color"],
                edgecolor="w",
                label=(
                    PART_PLOT_DATA[vol.part_name]["label"]
                    if vol.part_name not in plotted_part_names
                    else None
                ),
                width=0.8 if size == "md" else (0.6 if size == "sm" else 1),
            )

            if size == "lg":
                fontsize = "5" if len(vol.name) < 4 else "3.5"
            else:
                fontsize = "6" if len(vol.name) < 4 else "5"

            ax.bar_label(
                p,
                labels=len(years) * [vol],
                label_type="center",
                fontsize=fontsize,
            )
            cumulative_counter += counter
            plotted_part_names.add(vol.part_name)

    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.yaxis.set_minor_locator(MultipleLocator(1))

    plt.ylabel("# Pagina’s")
    plt.xlabel("Conceptiejaar" if date_type == "orig" else "Publicatiejaar")
    plt.legend()
    plt.tight_layout()
    part_postfix = "_" + "-".join(sorted(include_parts)) if include_parts else ""
    corr_postfix = "" if include_corrections else "_uncorrected"
    plt.savefig(f"figures/phusis-{date_type}{part_postfix}{corr_postfix}.png", dpi=500)


def plot_pie_chart(include_corrections=True):
    print(
        "Plotting pie chart", "without corrections" if not include_corrections else ""
    )
    index = get_index(include_corrections)

    lengths = {part_name: 0 for part_name in PART_PLOT_DATA.keys()}
    colors = [part["color"] for part in PART_PLOT_DATA.values()]
    labels = [part["label"] for part in PART_PLOT_DATA.values()]

    for volume in index.volumes:
        lengths[volume.part_name] += len(volume)

    _, ax = plt.subplots()
    ax.pie(
        lengths.values(),
        colors=colors,
        labels=labels,
        autopct="%1.1f%%",
        wedgeprops={
            "edgecolor": "w",
            "linewidth": 2,
            "linestyle": "solid",
            "antialiased": True,
        },
    )

    plt.tight_layout()
    plt.savefig(
        f"figures/phusis-pie-chart{'_uncorrected' if not include_corrections else ''}.png",
        dpi=500,
    )


if __name__ == "__main__":
    plot_histogram(size="lg")
    plot_histogram(size="lg", include_corrections=False)
    plot_histogram(date_type="pub")
    plot_histogram(include_parts=["lectures"], size="sm")
    plot_histogram(include_parts=["unpublished", "notes"])
    plot_histogram(date_type="ga")
    plot_pie_chart()
    plot_pie_chart(include_corrections=False)
