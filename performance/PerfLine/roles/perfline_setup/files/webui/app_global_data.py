from flask import Flask
from plumbum import local

from core import task_cache
exec(open('./../perfline.conf').read())

hostname = local["hostname"]["-s"]().strip()
app = Flask(__name__)
cache = task_cache.TaskCache()
report_resource_map = dict()
