from api import dlq


def test_add_to_dlq():
    dlq.add_to_dlq("url")
    assert dlq.DEAD_LETTER_QUEUE.get_nowait() == "url"


def test_add_to_no_admin_dlq():
    dlq.add_to_no_admin_dlq("site-id")
    assert dlq.NO_ADMIN_DEAD_LETTER_QUEUE.get_nowait() == "site-id"


def test_unload_dlq():
    dlq.add_to_dlq("url")
    assert list(dlq.unload_dlq(dlq.DEAD_LETTER_QUEUE)) == ["url"]


def test_log_unprocessed_dlq(capsys):
    dlq.add_to_dlq("url")
    dlq.log_unprocessed_dlq()
    captured = capsys.readouterr()
    assert "The following urls were not processed:\nurl" in captured.out


def test_log_no_admin_dlq(capsys):
    dlq.add_to_no_admin_dlq("site-id")
    dlq.log_no_admin_dlq()
    captured = capsys.readouterr()
    assert "Admin area could not be identified for these sites:\nsite-id" in captured.out
