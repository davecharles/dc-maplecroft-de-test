from flask_restful import Resource
from flask_jwt_extended import jwt_required
from api.api.schemas import SiteSchema
from api.models import Site
from api.commons.pagination import paginate

from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument(
    "admin_area",
    type=str,
    help="List sites within a Geo Boundaries admin area"
)


class SiteList(Resource):

    method_decorators = [jwt_required()]

    def get(self):
        """Get all Sites.

        Optionally, accepts a query parameter `?admin_area`, if specified
        only lists sites within the admin area.
        """
        schema = SiteSchema(many=True)
        query = Site.query
        args = parser.parse_args()
        if admin_area := args.get("admin_area"):
            return paginate(query.filter_by(admin_area=admin_area), schema)
        return paginate(query, schema)
