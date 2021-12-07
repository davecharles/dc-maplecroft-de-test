"""Extract-Transform-Load Helpers."""
import itertools
import typing

import click
import grequests

from api import dlq


def on_fail(request: grequests.AsyncRequest, exception: Exception):
    """Request fail callback."""
    click.echo(f"Request failed for {request.url}, reason:{exception}")
    dlq.add_to_dlq(request.url)


def chunk(
    g: typing.Generator[typing.Any, None, None], chunk_size: int
) -> typing.Iterator:
    """Enable chunk consumption of a generator.

    Pops first element to guarantee StopIteration when generator exhausted,
    then concatenates first item back before yield if generator not exhausted.
    """
    for first in g:
        rest_of_chunk = itertools.islice(g, 0, chunk_size - 1)
        yield itertools.chain([first], rest_of_chunk)


def get_resource_name(resource_url):
    """Given a URL return resource element.

    e.g. https://foo.com/bar.json -> bar.json
    """
    return resource_url.rsplit("/", 1)[-1]
