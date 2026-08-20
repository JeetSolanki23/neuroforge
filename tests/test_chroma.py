import pytest
from neuroforge.memory.chroma import health_check, init_chroma, get_collection, VALID_COLLECTIONS


@pytest.fixture(autouse=True)
def setup_chroma_path(tmp_path, monkeypatch):
    persist_dir = str(tmp_path / "chroma_db")
    monkeypatch.setattr("neuroforge.config.config.CHROMA_PERSIST_PATH", persist_dir)
    return persist_dir


def test_init_chroma_creates_collections():
    client = init_chroma()
    collections = [col.name for col in client.list_collections()]
    for name in VALID_COLLECTIONS:
        assert name in collections


def test_health_check_returns_true_after_init():
    init_chroma()
    assert health_check() is True


def test_get_collection_valid():
    for name in VALID_COLLECTIONS:
        col = get_collection(name)
        assert col.name == name


def test_get_collection_invalid():
    with pytest.raises(ValueError, match="Collection 'xyz' is not a valid collection name."):
        get_collection("xyz")
