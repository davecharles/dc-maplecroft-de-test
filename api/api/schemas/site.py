from api.models import Site
from api.extensions import ma, db


class SiteSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Site
        sqla_session = db.session
        load_instance = True
