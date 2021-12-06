from api.extensions import db


class Site(db.Model):
    """Site model.

    Defines a City bikes station.
    """
    # id is concatenation of parent network location ID and the station ID
    id = db.Column(db.String(255), primary_key=True)
    # Parent network location city
    city = db.Column(db.String(80), nullable=False)
    # Parent network country as ISO 3166 alpha 3 country code
    country = db.Column(db.String(3), nullable=False)
    # Station latitude
    latitude = db.Column(db.Float, nullable=False)
    # Station longitude
    longitude = db.Column(db.Float, nullable=False)
    # Station name
    name = db.Column(db.String(255), nullable=True)
    # Station data update time
    timestamp = db.Column(db.DateTime, nullable=True)
    # Bikes used (empty_slots)
    used = db.Column(db.Integer, default=0)
    # Bikes available (free_bikes)
    available = db.Column(db.Integer, default=0)
    # GeoBoundaries admin area as determined by this service
    admin_area = db.Column(db.String(255), nullable=True)
