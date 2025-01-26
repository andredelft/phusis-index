import re
from typing import Self
from functools import cache

from utils import volume_sort_key, find_closest_preceding_number
from load import load_index_yaml, load_parts_yaml, load_dates_yaml
from consts import ReferenceObj, IndexObj, DatesObj, VolumeName


REF_REGEX = re.compile(r"^(?P<start>\d+)(?:-(?P<end>\d+)|(?P<suffix>f{1,2})\.?)?$")


class InvalidReference(Exception):
    pass


class Reference:
    def __init__(
        self,
        start: int,
        end: int | None = None,
        categories: set[str] = set(),
    ):
        self.start = start
        self.end = end
        self.categories = categories

    def __str__(self):
        if not self.end:
            return str(self.start)
        elif self.end - self.start <= 2:
            return f"{self.start}{'f' * (self.end - self.start)}"
        else:
            return f"{self.start}-{self.end}"

    def __repr__(self):
        category_str = ", ".join(sorted(self.categories))

        return f'<Reference {self}{f": {category_str}" if self.categories else ""}>'

    def __eq__(self, other: Self):
        return self.start == other.start and self.end == other.end

    def __lt__(self, other: Self):
        if self.start == other.start:
            if not other.end:
                return False
            elif not self.end:
                return True
            else:
                return self.end < other.end
        else:
            return self.start < other.start

    def __len__(self):
        if not self.end:
            return 1
        else:
            return self.end - self.start + 1

    @classmethod
    def from_yaml(cls, yaml: ReferenceObj):
        if isinstance(yaml, dict):
            if len(yaml) != 1:
                raise ValueError(f"Reference has invalid format: {yaml}")

            reference, categories = next(item for item in yaml.items())

            ref_str = str(reference)

            if isinstance(categories, str):
                raise DeprecationWarning(
                    f"Category '{categories}' must be contained in a list"
                )

            categories = set(categories)
        else:
            ref_str = str(yaml)
            categories: set[str] = set()

        m = REF_REGEX.match(ref_str)

        if not m:
            raise InvalidReference(f"Reference '{ref_str}' is invalid")

        start, end, suffix = m.groups()

        start = int(start)

        if end:
            end = int(end)
        elif suffix:
            end = start + len(suffix)
        else:
            end = None

        return cls(start, end, categories)


class Volume:
    def __init__(self, name: str, references: list[Reference]):
        self.name = name
        self.references = sorted(references)
        self._sort_key = volume_sort_key(self.name)

        self.part_name = next(
            part.name
            for part in get_parts()
            if part.start <= self._sort_key[0] <= part.end
        )

    def __len__(self):
        return sum(len(r) for r in self.references)

    def __iter__(self):
        for reference in self.references:
            yield reference

    def __eq__(self, other: Self):
        return self._sort_key == other._sort_key

    def __lt__(self, other: Self):
        return self._sort_key < other._sort_key

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Volume {self} ({len(self.references)} references)>"

    @classmethod
    def from_yaml(cls, name: VolumeName, yaml: list[ReferenceObj]):
        return cls(str(name), [Reference.from_yaml(item) for item in yaml])


class Index:
    def __init__(self, volumes: list[Volume]):
        self.volumes = sorted(volumes)

        self._index = {volume.name: volume for volume in volumes}
        self.parts: dict[str, list[Volume]] = {part.name: [] for part in get_parts()}

        for volume in volumes:
            self.parts[volume.part_name].append(volume)

    def __len__(self):
        return sum(len(volume) for volume in self.volumes)

    def __iter__(self):
        for volume in self.volumes:
            yield volume

    def __getitem__(self, key: str | int):
        return self._index[str(key)]

    def __repr__(self):
        return f"<Index ({len(self.volumes)} volumes)>"

    @property
    def references(self):
        for volume in self:
            for reference in volume:
                yield volume, reference

    @property
    def categories(self):
        return sorted(set().union(*[ref.categories for _, ref in self.references]))

    @classmethod
    def from_yaml(cls, yaml: IndexObj):
        volumes = [Volume.from_yaml(*item) for item in yaml.items()]
        return cls(volumes)


def in_range(year: int | None, min_year: int | None, max_year: int | None):
    if min_year == None and max_year == None:
        return True

    if year == None:
        return False

    if min_year != None and year < min_year:
        return False

    if max_year != None and year > max_year:
        return False

    return True


class Dating:
    def __init__(self, vol_page_year_mapping: dict[str, dict[int, int | None]]):
        self._vol_page_year_mapping = vol_page_year_mapping

    def __getitem__(self, key: str):
        return self._vol_page_year_mapping.get(key)

    def filter(self, index: Index, min_year: int = None, max_year: int = None):
        """Filters a given index according to specified conditions and returns a new `Index` instance"""
        filtered_volumes = []

        for volume in index.volumes:
            filtered_references = []

            for reference in volume.references:
                year = self.get_year(volume, reference)

                if in_range(year, min_year, max_year):
                    filtered_references.append(reference)

            if filtered_references:
                filtered_volumes.append(Volume(volume.name, filtered_references))

        return Index(filtered_volumes)

    def get_year(self, volume: Volume, reference: Reference):
        page_year_mapping = self[volume.name]

        if not page_year_mapping:
            return None

        page_key = find_closest_preceding_number(
            list(page_year_mapping.keys()), reference.start
        )

        if page_key == None:
            return None

        return page_year_mapping[page_key]

    @classmethod
    def from_yaml(cls, yaml: DatesObj):
        vol_page_year_mapping = {}

        for vol_name, value in yaml.items():
            if not isinstance(value, dict):
                vol_page_year_mapping[str(vol_name)] = {1: value}
            else:
                vol_page_year_mapping[str(vol_name)] = value

        return cls(vol_page_year_mapping)


class Part:
    def __init__(self, name: str, start: int, end: int):
        self.name = name
        self.start = start
        self.end = end


@cache
def get_index(include_corrections=True):
    return Index.from_yaml(load_index_yaml(include_corrections))


@cache
def get_dating(date_type: str = "orig"):
    return Dating.from_yaml(load_dates_yaml(date_type))


@cache
def get_parts():
    parts = load_parts_yaml()
    return [Part(**part) for part in parts]
