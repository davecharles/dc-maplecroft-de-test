"""Default configuration.

Use env var to override
"""
import os

ENV = os.getenv("FLASK_ENV")
DEBUG = ENV == "development"
SECRET_KEY = os.getenv("SECRET_KEY")

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False

CITY_BIKE_URI = os.getenv(
    "APP_CITY_BIKE_URI", "https://api.citybik.es"
)
GEO_BOUNDARIES_URI = os.getenv(
    "APP_GEO_BOUNDARIES_URI", "https://www.geoboundaries.org/gbRequest.html"
)
ADMIN_AREA_LEVEL = os.getenv("APP_ADMIN_AREA_LEVEL", "ADM3")
NO_ADMIN_AREA = os.getenv("APP_NO_ADMIN_AREA", "NO-ADMIN")
SITE_CHUNK_SIZE = int(os.getenv("APP_SITE_CHUNK_SIZE", 10))
RESPONSE_TIMEOUT_SECONDS = float(os.getenv("APP_RESPONSE_TIMEOUT_SECONDS", 0.5))
PROCESSING_RETRY_COUNT = int(os.getenv("APP_PROCESSING_RETRY_COUNT", 3))

# Uncomment to enable ?jwt=TOKEN query string
# JWT_TOKEN_LOCATION = ["headers", "query_string"]
