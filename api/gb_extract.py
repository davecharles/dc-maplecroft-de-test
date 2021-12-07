"""Geo Boundaries API extraction."""
import click
import grequests
import json
import typing

from flask import current_app

from api import etl_utils


def decrement_adm(adm: str) -> str:
    """Decrement admin level.

    Given an admin level, returns next one down. Raises `KeyError`
    if admin level not recognised, or AMD0 supplied.
    """
    return {
        "ADM3": "ADM2",
        "ADM2": "ADM1",
        "ADM1": "ADM0",
    }[adm]


def fetch_geoboundary_resource(geo_resource_url: str) -> dict:
    """Fetch geoboundary resource.

    Loads a geoboundary resource and stores a local copy.
    """
    click.echo(f"Fetching geoboundary features from: {geo_resource_url}")
    rs = (grequests.get(u) for u in [geo_resource_url])
    response = list(grequests.imap(rs))[0]
    with open(f"data/{etl_utils.get_resource_name(geo_resource_url)}", "w") as f:
        f.write(response.text)
    return response.json()


def get_geoboundary_features(geo_resource_url) -> typing.Generator[dict, None, None]:
    """Get geoboundary features.

    Given a geoboundary resource URL, checks for local copy. If not available,
    requests the resource. In either case, returns a list of geoboundary
    resource features as a generator.
    """
    resource_name = etl_utils.get_resource_name(geo_resource_url)
    try:
        with open(f"data/{resource_name}") as f:
            data = json.load(f)
        click.echo(f"Using cache for: {resource_name}")
    except FileNotFoundError:
        click.echo(f"No cached features for: {resource_name}")
        data = fetch_geoboundary_resource(geo_resource_url)
    return (feature for feature in data["features"])


def fetch_geoboundary_url(country_code: str) -> str:
    """Fetch geoboundary URL.

    Given a country code, load a geoboundary resource for `ADMIN_AREA_LEVEL`
    and extract `gjDownloadURL` URL.
    """
    click.echo(f"Fetching geoboundary resource for {country_code}")
    geoboundary_uri = current_app.config.get("GEO_BOUNDARIES_URI")
    admin_area_level = current_app.config.get("ADMIN_AREA_LEVEL")
    while True:
        url = f"{geoboundary_uri}?ISO={country_code}&ADM={admin_area_level}"
        click.echo(f"Using URL: {url}")
        request = grequests.get(url).send()

        # rs = (grequests.get(u) for u in [url])  # TODO REMOVE
        # response = list(grequests.imap(rs))[0]

        if len(request.response.json()):
            break
        click.echo(f"{admin_area_level} not available, downgrading")
        admin_area_level = decrement_adm(admin_area_level)
    return request.response.json()[0]["gjDownloadURL"]


def load_geoboundary_data(country_code) -> typing.Iterator[dict]:
    """Load geoboundary data."""
    try:
        geo_resource_url = fetch_geoboundary_url(country_code)
        return get_geoboundary_features(geo_resource_url)
    except KeyError as e:
        click.echo(f"Key error while loading geoboundary data for: {country_code}")
        click.echo(f"tip: this could mean there is no ADM data for this country")
        return iter(())
