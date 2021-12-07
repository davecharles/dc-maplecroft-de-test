from flask import url_for


def test_get_sites(client, db, site_factory, admin_headers):
    sites_url = url_for('api.sites')
    sites = site_factory.create_batch(10)

    db.session.add_all(sites)
    db.session.commit()

    rep = client.get(sites_url, headers=admin_headers)
    assert rep.status_code == 200

    results = rep.get_json()
    for site in sites:
        assert any(s["id"] == site.id for s in results["results"])


def test_get_sites_by_admin(client, db, site, site_factory, admin_headers):
    sites = site_factory.create_batch(10)
    sites_url = url_for('api.sites') + "?admin_area=AREA-51"

    db.session.add_all(sites)
    db.session.add(site)
    db.session.commit()

    rep = client.get(sites_url, headers=admin_headers)
    assert rep.status_code == 200

    results = rep.get_json()
    assert len(results["results"]) == 1
