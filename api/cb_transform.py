"""City Bike data transformation."""
import click
from flask import current_app
from shapely.geometry import shape, Point

from api.extensions import db
from api.models.site import Site

from api import dlq
from api import gb_extract


def process_admin_areas():
    """Process admin area for all sites."""
    click.echo("Processing admin areas from Site data")
    sites = Site.query.filter_by(admin_area=None).all()
    click.echo(f"{len(sites)} sites identified with no admin area")
    for site in sites:
        if not identify_admin_area(site):
            dlq.add_to_no_admin_dlq(site.id)


def update_site_admin_area(site: Site, shape_id: str):
    """Save identified shape ID as Site admin area."""
    site.admin_area = shape_id
    db.session.merge(site)
    db.session.commit()


def poly_check(latitude: float, longitude: float, area: str) -> bool:
    """Check if a coordinate is within an area."""
    point = Point([longitude, latitude])  # Notice reverse Lat/Long order
    return point.within(area)


def identify_admin_area(site: Site) -> bool:
    """Identify admin area.

    Iterates over extracted geoboundary features, builds a `shape` from the
    feature geometry and checks if sites coords are within the feature area.
    Mark sites whose admin area could not be established to enable reprocessing.
    """
    click.echo(f"Identifying admin area for Site: {site.id}")
    features = gb_extract.load_geoboundary_data(site.country)
    for feature in features:
        shape_id = feature["properties"]["shapeID"]
        area = shape(feature["geometry"])
        if not poly_check(site.latitude, site.longitude, area):
            continue
        update_site_admin_area(site, shape_id)
        click.echo(f"Identified admin area for Site {site.id}: {shape_id}")
        return True
    # Unable to identify admin area, annotate accordingly
    update_site_admin_area(site, current_app.config.get("NO_ADMIN_AREA"))
    return False
