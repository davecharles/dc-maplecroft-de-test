"""Dead Letter Queues.

- DEAD_LETTER_QUEUE: unprocessed URLs
- NO_ADMIN_DEAD_LETTER_QUEUE: Untransformed Site ids.
"""
import queue
import typing

import click


DEAD_LETTER_QUEUE = queue.Queue()
NO_ADMIN_DEAD_LETTER_QUEUE = queue.Queue()


def add_to_dlq(url: str):
    """Add item to DEAD_LETTER_QUEUE."""
    click.echo(f"Adding url to dead letter queue: {url}")
    DEAD_LETTER_QUEUE.put(url)


def add_to_no_admin_dlq(site_id: str):
    """Add item to NO_ADMIN_DEAD_LETTER_QUEUE."""
    click.echo(f"Adding site to admin dead letter queue: {site_id}")
    NO_ADMIN_DEAD_LETTER_QUEUE.put(site_id)


def unload_dlq(dlq: queue.Queue) -> typing.Generator[str, None, None]:
    """Dequeue a DLQ to iterable."""
    items = []
    while True:
        try:
            items.append(dlq.get_nowait())
        except queue.Empty:
            break
    return (item for item in items)


def log_unprocessed_dlq():
    """Log all DEAD_LETTER_QUEUE items."""
    retry_urls = "\n".join(list(unload_dlq(DEAD_LETTER_QUEUE)))
    click.echo(f"The following urls were not processed:\n{retry_urls}")


def log_no_admin_dlq():
    """Log all NO_ADMIN_DEAD_LETTER_QUEUE items."""
    no_admin_area_sites = "\n".join(list(unload_dlq(NO_ADMIN_DEAD_LETTER_QUEUE)))
    click.echo(f"Admin area could not be identified these sites:\n{no_admin_area_sites}")
