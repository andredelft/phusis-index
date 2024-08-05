import re
from typing import Self

from utils import volume_sort_key
from load import get_parts, ReferenceObj, IndexObj


REF_REGEX = re.compile(r"^(?P<start>\d+)(?:-(?P<end>\d+)|(?P<suffix>f{1,2})\.?)?$")


class InvalidReference(Exception):
    pass


class Reference(object):
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

            if isinstance(categories, list):
                categories = set(categories)
            else:
                categories = {categories}
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

        self.part = next(
            part["name"]
            for part in get_parts()
            if part["start"] <= self._sort_key[0] <= part["end"]
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
    def from_yaml(cls, name: str, yaml: list[ReferenceObj]):
        return cls(name, [Reference.from_yaml(item) for item in yaml])


class Index:
    def __init__(self, volumes: list[Volume]):
        self.volumes = sorted(volumes)

    def __len__(self):
        return sum(len(volume) for volume in self.volumes)

    def __iter__(self):
        for volume in self.volumes:
            yield volume

    def __repr__(self):
        return f"<Index ({len(self.volumes)} volumes)>"

    @classmethod
    def from_yaml(cls, yaml: IndexObj):
        volumes = [Volume.from_yaml(*item) for item in yaml.items()]
        return cls(volumes)
