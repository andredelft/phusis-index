import yaml
from pathlib import Path


from index import get_index, get_dating, Index, Dating


def by_year(index: Index, dating: Dating):

    data = {}

    for vol in index.volumes:
        for ref in vol:
            year = str(dating.get_year(vol, ref))

            year_dict = data.get(year, {})
            vol_list = year_dict.get(vol.name, [])
            vol_list.append(str(ref))

            year_dict[vol.name] = vol_list
            data[year] = year_dict

    return data


if __name__ == "__main__":
    index = get_index()
    dating = get_dating("orig")

    data = by_year(index, dating)

    with open(Path("aggregates", "by-year.yml"), "w") as f:
        yaml.safe_dump(data, f)

    categories = set()

    for vol in index:
        for ref in vol.references:
            categories.update(ref.categories)

    with open(Path("aggregates", "categories.yml"), "w") as f:
        yaml.safe_dump(sorted(categories), f)
