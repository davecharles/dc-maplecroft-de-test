import datetime
import json
import pytest
from pytest_factoryboy import register
from unittest.mock import Mock

from dotenv import load_dotenv
from shapely.geometry import shape, Point

from api.models import User, Site
from api.app import create_app
from api.extensions import db as _db
from api import gb_extract as gbe

from tests.factories import UserFactory, SiteFactory

register(UserFactory)
register(SiteFactory)


@pytest.fixture(scope="session")
def app():
    load_dotenv(".testenv")
    app = create_app(testing=True)
    return app


@pytest.fixture
def db(app):
    _db.app = app

    with app.app_context():
        _db.create_all()

    yield _db

    _db.session.close()
    _db.drop_all()


@pytest.fixture
def admin_user(db):
    user = User(
        username='admin',
        email='admin@admin.com',
        password='admin'
    )

    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture
def admin_headers(admin_user, client):
    data = {
        'username': admin_user.username,
        'password': 'admin'
    }
    rep = client.post(
        '/auth/login',
        data=json.dumps(data),
        headers={'content-type': 'application/json'}
    )

    tokens = json.loads(rep.get_data(as_text=True))
    return {
        'content-type': 'application/json',
        'authorization': 'Bearer %s' % tokens['access_token']
    }


@pytest.fixture
def admin_refresh_headers(admin_user, client):
    data = {
        'username': admin_user.username,
        'password': 'admin'
    }
    rep = client.post(
        '/auth/login',
        data=json.dumps(data),
        headers={'content-type': 'application/json'}
    )

    tokens = json.loads(rep.get_data(as_text=True))
    return {
        'content-type': 'application/json',
        'authorization': 'Bearer %s' % tokens['refresh_token']
    }


@pytest.fixture
def site(db):
    s = Site(
        id="copenhagen-1234",
        city="Copenhagen",
        country="DNK",
        latitude=55.1,
        longitude=12.5,
        name="station",
        timestamp=datetime.datetime.utcnow(),
        used=1,
        available=0,
        admin_area="AREA-51",
    )
    db.session.add(s)
    db.session.commit()
    return s


@pytest.fixture
def chunkable_generator_int():
    return (i for i in range(14))


@pytest.fixture
def chunkable_generator_str():
    return ("url" for i in range(14))


@pytest.fixture
def coords():
    return [[[[0.0, 0.0],
       [0.0, 10.0],
       [10.0, 10.0],
       [10.0, 0.0],
       ]]]


@pytest.fixture
def area(coords):
    return shape(
        {
            "type": "MultiPolygon",
            "coordinates": coords,
         }

    )


@pytest.fixture
def features(coords):
    feature = {
        "type": "Feature",
        "properties": {
            "shapeName": "Castelletto Monferrato",
            "shapeISO": "None",
            "shapeID": "ITA-ADM3-3_0_0-B1",
            "shapeGroup": "ITA", "shapeType": "ADM3"
        },
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": coords,
        }
    }
    return [feature, feature, feature]


@pytest.fixture
def fake_load_geoboundary_data(monkeypatch, features):
    def mock_meth(*args, **kwargs):
        return features
    monkeypatch.setattr(gbe, "load_geoboundary_data", mock_meth)
