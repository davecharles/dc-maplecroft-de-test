import pytest

from api import etl_utils as eu


def test_chunk(chunkable_generator_int):
    items = list(next(eu.chunk(chunkable_generator_int, chunk_size=5)))
    assert len(items) == 5
    items = list(next(eu.chunk(chunkable_generator_int, chunk_size=5)))
    assert len(items) == 5
    items = list(next(eu.chunk(chunkable_generator_int, chunk_size=5)))
    assert len(items) == 4
    with pytest.raises(StopIteration):
        list(next(eu.chunk(chunkable_generator_int, chunk_size=5)))
