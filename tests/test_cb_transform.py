from api import cb_transform as cbt
from api.models import Site


def test_update_site_admin_area(site, db):
    assert site.admin_area == "AREA-51"
    cbt.update_site_admin_area(site, "ROSWELL")
    assert Site.query.get(site.id).admin_area == "ROSWELL"


def test_poly_check(area):
    assert cbt.poly_check(5.0, 5.0, area)
    assert not cbt.poly_check(5.0, 11.0, area)


def test_identify_admin_area(site, fake_load_geoboundary_data):
    site.latitude = 1.0  # Inside coords fixture
    site.longitude = 9.0
    assert cbt.identify_admin_area(site)


def test_identify_admin_area_fail_outside(site, fake_load_geoboundary_data):
    site.latitude = -1.0  # Outside coords fixture
    site.longitude = 11.0
    assert not cbt.identify_admin_area(site)
