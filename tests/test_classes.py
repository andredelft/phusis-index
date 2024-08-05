from classes import *
import pytest


@pytest.fixture
def references():
    r1 = Reference.from_yaml({"28": "Her123"})
    r2 = Reference.from_yaml("23ff.")
    r3 = Reference.from_yaml({"30-35": ["Her123", "PhuTex"]})

    return r1, r2, r3


@pytest.fixture
def volume(references):
    return Volume("6.1", references)


@pytest.fixture
def index():
    return Index.from_yaml(
        {"6.1": [{"28": "Her123"}, "23ff."], "3": [{"30-35": ["Her123", "PhuTex"]}]}
    )


def test_references(references):
    r1, r2, r3 = references

    assert len(r1) == 1
    assert len(r2) == 3
    assert len(r3) == 6

    assert r1.categories == {"Her123"}
    assert r2.categories == set()
    assert r3.categories == {"Her123", "PhuTex"}


def test_volume(volume):
    assert volume.name == "6.1"
    assert len(volume) == 10
    assert [str(r) for r in volume] == ["23ff", "28", "30-35"]


def test_index(index):
    assert len(index) == 10
    assert [str(v) for v in index] == ["3", "6.1"]
