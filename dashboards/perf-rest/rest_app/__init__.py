from flask_restx import Api
from .performance import api as perf_apis

api = Api(title="Performance MongoDB APIs", version="1.0", description="REST APIs to access Performance MongoDB.")

api.add_namespace(perf_apis)

