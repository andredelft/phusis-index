import yaml
from pathlib import Path
from yaml_to_markdown.md_converter import MDConverter

from utils import category_sort_key
from index import get_index, get_dating, Index, Dating


def by_year(index: Index, dating: Dating):
    data = {}

    for vol, ref in index.references:
        year = str(dating.get_year(vol, ref))

        year_dict = data.get(year, {})
        vol_list = year_dict.get(vol.name, [])
        vol_list.append(str(ref))

        year_dict[vol.name] = vol_list
        data[year] = year_dict

    return data


def by_category(index: Index):
    term_index = {}
    bibliography_index = {}

    for vol, ref in index.references:
        ref_str = f"{vol}, {ref}"

        for category in ref.categories:
            if ":" in category:
                current_node = bibliography_index
                for ref_part in category.split(":"):
                    current_node[ref_part] = current_node.get(ref_part, {})
                    current_node = current_node[ref_part]

                current_node["_"] = current_node.get("_", [])
                current_node["_"].append(ref_str)
            else:
                term_index[category] = term_index.get(category, [])
                term_index[category].append(ref_str)

    bibliography = {
        author: list(works.keys()) for (author, works) in bibliography_index.items()
    }

    return term_index, bibliography_index, bibliography


def by_category_and_year(index: Index, dating: Dating):
    term_index = {}
    bibl_index = {}

    for vol, ref in index.references:
        year = dating.get_year(vol, ref)
        vol_str = vol.name

        for category in ref.categories:
            if ":" in category:
                author, work, *_ = category.split(":")
                print(author, work)

                bibl_index[author] = bibl_index.get(author, {})
                bibl_index[author][work] = bibl_index[author].get(work, {})
                entry = bibl_index[author][work]

            else:
                term_index[category] = term_index.get(category, {})
                entry = term_index[category]

            entry[year] = entry.get(year, {})
            entry[year][vol_str] = entry.get(vol_str, [])
            entry[year][vol_str].append(str(ref))

    return term_index, bibl_index


def format_entry(entry):
    return "; ".join(f'GA {vol}: {", ".join(refs)}' for (vol, refs) in entry.items())


def format_term_index(term_index, category_aliases):
    formatted_categories = []

    for category in sorted(
        term_index.keys(), key=lambda c: category_aliases[c]["sort_key"]
    ):
        formatted_category = f"{category_aliases[category]['label']}"
        for year, entry in sorted(term_index[category].items()):
            formatted_category += f"\n  {year}:\n    {format_entry(entry)}"

        formatted_categories.append(formatted_category)

    return "\n".join(formatted_categories)


def format_bibl_index(bibl_index, category_aliases):
    authors = []

    for author in sorted(
        bibl_index.keys(), key=lambda c: category_aliases[c]["sort_key"]
    ):
        formatted_author = category_aliases[author]["label"] + "\n\n"

        formatted_works = []

        for work in sorted(
            bibl_index[author].keys(),
            key=lambda c: category_aliases[f"{author}:{c}"]["sort_key"],
        ):
            formatted_work = category_aliases[f"{author}:{work}"]["label"]

            for year, entry in sorted(bibl_index[author][work].items()):
                formatted_work += f"\n  {year}:\n    {format_entry(entry)}"

            formatted_works.append(formatted_work)

        formatted_author += "\n".join(formatted_works)
        authors.append(formatted_author)

    return "\n\n".join(authors)


def generate_category_aliases(index: Index, max_level=2):
    category_aliases = {}

    for category in index.categories:
        category_parts = category.split(":")

        for n in range(1, min(max_level, len(category_parts)) + 1):
            cat = ":".join(category_parts[:n])

            category_aliases[cat] = {
                "label": cat.replace("-", " "),
                "sort_key": category_sort_key(cat),
            }

    return category_aliases


if __name__ == "__main__":
    index = get_index()
    dating = get_dating("orig")

    save_folder = Path("aggregates")
    md_converter = MDConverter()

    def save_as_yaml(obj: dict, filename: str):
        with open(save_folder / filename, "w") as f:
            yaml.safe_dump(obj, f, allow_unicode=True)

    save_as_yaml(by_year(index, dating), "by-year.yml")

    term_index, bibliography_index, bibliography = by_category(index)

    save_as_yaml(term_index, "term-index.yml")
    save_as_yaml(bibliography_index, "bibliography-index.yml")
    save_as_yaml(bibliography, "bibliography.yml")

    # Category aliases

    category_aliases_file = save_folder / "category-aliases.yml"

    if category_aliases_file.exists():
        with open(category_aliases_file) as f:
            category_aliases = yaml.safe_load(f)
    else:
        category_aliases = {}

    category_aliases = {
        **generate_category_aliases(index),
        **category_aliases,
    }

    save_as_yaml(category_aliases, "category-aliases.yml")

    # Filtered index

    save_folder /= "1934"
    save_folder.mkdir(parents=True, exist_ok=True)

    filtered_index = dating.filter(index, max_year=1934)
    term_index, bibl_index = by_category_and_year(filtered_index, dating)
    formatted_index = format_term_index(term_index, category_aliases)
    formatted_bibl_index = format_bibl_index(bibl_index, category_aliases)

    with open(save_folder / "index.txt", "w") as f:
        f.write(formatted_index)

    with open(save_folder / "bibliography-index.txt", "w") as f:
        f.write(formatted_bibl_index)
