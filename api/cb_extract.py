"""City Bike API extraction."""
import typing

from dateutil.parser import parse
import click
import country_converter
import grequests
from sqlalchemy import exc

from api.extensions import db
from api.models.site import Site

from api import dlq
from api import etl_utils


class MakeSiteError(Exception):
    """Exception raised when site create/update fails."""


def load_master_site_urls(uri: str) -> typing.Generator[str, None, None]:
    """Load master site URLs.

    Gets `href` and `location` for all City Bike networks. This request seeds
    the entire ETL process, so if it fails all bets are off. The orchestration
    of this pipeline should cater for such failures.
    """
    filter_uri = f"{uri}/v2/networks/?fields=href,location"
    request = grequests.get(filter_uri).send()
    if hasattr(request, "exception"):
        raise request.exception()
    elif not request.response.ok:
        raise RuntimeError(
            f"Load master sites failed: {request.response.status_code}"
        )
    else:
        master_sites = (
            f"{uri}{network['href']}" for network in request.response.json()["networks"]
        )
        return master_sites


def make_sites(response: typing.Any):
    """Make site data.

    Given a request response, create or update a Site model. Converts the
    ISO 3166 alpha 2 country code to ISO 3166 alpha 3.
    """
    data = response.json()
    network = data["network"]
    network_id = network["id"]
    location = network["location"]
    city = location["city"]
    country_alpha2 = location["country"]
    country = country_converter.convert(names=[country_alpha2], to='ISO3')
    stations = network["stations"]
    click.echo(
        f"Processing site at {response.url}: {len(stations)} station(s)"
    )
    for station in stations:
        try:
            site = Site(
                id=f"{network_id}-{station['id']}",
                city=city,
                country=country,
                latitude=station["latitude"],
                longitude=station["longitude"],
                name=station["name"],
                timestamp=parse(station["timestamp"]),
                used=station["empty_slots"],
                available=station["free_bikes"],
            )
            db.session.merge(site)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            raise MakeSiteError(f"Failed to save site: {e}")


def process(response: typing.Any):
    """Process a site.

    Given a request response, make a Site. If response fails add url to
    dead letter queue.
    """
    if response is None:
        return
    if not response.ok:
        click.echo(f"Bad response {response.status_code} for {response.url}")
        dlq.add_to_dlq(response.url)
        return
    try:
        make_sites(response)
    except (MakeSiteError, KeyError) as e:
        click.echo(f"Error processing site at {response.url}: {e}")
        dlq.add_to_dlq(response.url)


def extract_sites(urls: list, timeout: float = 0.5):
    """Extract Citybike sites."""
    rs = (grequests.get(u, timeout=timeout) for u in urls)
    responses = grequests.imap(rs, exception_handler=etl_utils.on_fail)
    for response in responses:
        process(response)


def process_chunk(
        g: typing.Generator[str, None, None],
        chunk_size: int = 10,
        timeout: float = 1.0) -> bool:
    """Process a chunk of URLs.

    Returns true if there is still work to do and false otherwise.
    """
    try:
        urls = list(next(etl_utils.chunk(g, chunk_size)))
    except StopIteration:
        click.echo(f"Chunks exhausted!")
        return False
    else:
        extract_sites(urls, timeout)
        return True
