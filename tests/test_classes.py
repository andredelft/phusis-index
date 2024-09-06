from index import *
import pytest


@pytest.fixture
def references():
    r1 = Reference.from_yaml({28: "Her123"})
    r2 = Reference.from_yaml("23ff.")
    r3 = Reference.from_yaml({"30-35": ["Her123", "techne"]})

    return r1, r2, r3


@pytest.fixture
def volume(references):
    return Volume("6.1", references)


@pytest.fixture
def index():
    return Index.from_yaml(
        {"6.1": [{28: "Her123"}, "23ff."], 3: [{"30-35": ["Her123", "techne"]}]}
    )


@pytest.fixture
def dating():
    return Dating.from_yaml({"6.1": {20: 1925, 28: 1930}, 3: 1935})


def test_references(references):
    r1, r2, r3 = references

    assert len(r1) == 1
    assert len(r2) == 3
    assert len(r3) == 6

    assert r1.categories == {"Her123"}
    assert r2.categories == set()
    assert r3.categories == {"Her123", "techne"}


def test_volume(volume):
    assert volume.name == "6.1"
    assert volume.part_name == "published"
    assert len(volume) == 10
    assert [str(r) for r in volume] == ["23ff", "28", "30-35"]


def test_index(index):
    assert len(index) == 10
    assert [str(v) for v in index] == ["3", "6.1"]
    assert index["3"].name == "3"
    assert len(index["6.1"]) == 4


def test_dates(index, dating):
    v1, v2 = index.volumes
    (r1,) = v1.references
    r2, r3 = v2.references

    print(dating._vol_page_year_mapping)

    assert dating.get_year(v1, r1) == 1935
    assert dating.get_year(v2, r2) == 1925
    assert dating.get_year(v2, r3) == 1930
