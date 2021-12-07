from api import cb_extract as cbe
from api import dlq


def test_process_chunk(request, capsys, chunkable_generator_str):
    def cleanup():
        assert len(list(dlq.unload_dlq(dlq.DEAD_LETTER_QUEUE))) == 14
    request.addfinalizer(cleanup)
    assert cbe.process_chunk(chunkable_generator_str, chunk_size=5)
    assert cbe.process_chunk(chunkable_generator_str, chunk_size=5)
    assert cbe.process_chunk(chunkable_generator_str, chunk_size=5)
    assert not cbe.process_chunk(chunkable_generator_str, chunk_size=5)
    captured = capsys.readouterr()
    assert "Chunks exhausted!" in captured.out
