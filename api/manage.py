import click
from flask import current_app
from flask.cli import with_appcontext

from api import cb_extract, cb_transform, dlq


@click.group()
def cli():
    """Main entry point"""


@cli.command("init")
@with_appcontext
def init():
    """Create a new admin user"""
    from api.extensions import db
    from api.models import User

    click.echo("create user")
    user = User(username="admin", email="admin@mail.com", password="admin", active=True)
    db.session.add(user)
    db.session.commit()
    click.echo("created user admin")


@cli.command("load_sites")
@with_appcontext
def load_sites():
    """Load sites.

    Extracts all the networks from `CITY_BIKE_URI` endpoint, and for each
    network extracts "Master Site" attributes including country code and the
    nested stations (i.e. "Sites"). For each Site the latitude/longitude
    and slot info is acquired.

    Citybike data specifies ISO 3166 alpha 2 country codes for each master Site
    so a conversion to ISO 3166 alpha 3 country code is performed for the
    purposes of the GeoBoundaries query.

    Each Site's admin area is determined by querying the relevant GeoBoundaries
    dataset, identified by the country code and setting value for
    `ADMIN_AREA_LEVEL` (e.g. `ADM3`). For example given:

    https://www.geoboundaries.org/gbRequest.html?ISO=GBR&ADM=ADM3

    A check is made for a cached GeoBoundaries dataset, otherwise a dataset is
    downloaded. Once loaded, for each `feature` in the GeoBoundaries dataset,
    if a Site's coordinates are within the feature shape's boundary then the
    Site's admin_area field is set accordingly, otherwise the next `feature`
    is checked.

    Processing is as follows:
        - Get all the Master Site URLs.
        - Process Master Site URLs in chunks of `SITE_CHUNK_SIZE`. This
          mitigates being throttled (HTTP 429) by the `CITY_BIKE_URI` endpoint.
        - For each URL in a chunk, determine admin area and save to Site model.

    Any failures are pushed to a dead letter queue using `add_to_dlq`.
    Once all Master Site URL chunks are exhausted the DLQ is processed.
    Reprocessing of the DLQ is repeated `PROCESSING_RETRY_COUNT` times.

    Similarly, if an admin area cannot be established for a Site, the Site's ID
    is pushed to a 'no admin' dead letter queue using `add_to_no_admin_dlq`.

    On exit, the details of any remaining items in both DLQs are logged.
    """
    click.echo("Loading master site data...")
    master_site_urls = cb_extract.load_master_site_urls(
        current_app.config.get("CITY_BIKE_URI")
    )
    timeout = current_app.config.get("RESPONSE_TIMEOUT_SECONDS")
    chunk_size = current_app.config.get("SITE_CHUNK_SIZE")
    click.echo(f"Extracting site data, chunk-size={chunk_size} timeout={timeout}")
    while cb_extract.process_chunk(
        master_site_urls, chunk_size=chunk_size, timeout=timeout
    ):
        cb_transform.process_admin_areas()

    # DLQ processing
    dlq_retries = current_app.config.get("PROCESSING_RETRY_COUNT")
    retry_urls = dlq.unload_dlq(dlq.DEAD_LETTER_QUEUE)
    for retry in range(dlq_retries):
        while cb_extract.process_chunk(
            retry_urls, chunk_size=chunk_size, timeout=timeout
        ):
            cb_transform.process_admin_areas()
        else:
            click.echo("DLQ cleared!")
            break
    else:
        dlq.log_unprocessed_dlq()
    dlq.log_no_admin_dlq()


if __name__ == "__main__":
    cli()
