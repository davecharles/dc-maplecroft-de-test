import datetime

import factory
from factory.fuzzy import FuzzyFloat, FuzzyDateTime, FuzzyInteger

from api.models import User, Site


class UserFactory(factory.Factory):

    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.Sequence(lambda n: "user%d@mail.com" % n)
    password = "mypwd"

    class Meta:
        model = User


class SiteFactory(factory.Factory):

    id = factory.Sequence(lambda n: "site-%d" % n)
    city = factory.Sequence(lambda n: "city-%d" % n)
    country = factory.Sequence(lambda n: "country-%d" % n)
    latitude = FuzzyFloat(50.0, 55.0)
    longitude = FuzzyFloat(11.0, 14.0)
    name = factory.Sequence(lambda n: "name-%d" % n)
    timestamp = FuzzyDateTime(
        datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=2)
    )
    used = FuzzyInteger(0, 12)
    available = FuzzyInteger(0, 12)

    class Meta:
        model = Site
