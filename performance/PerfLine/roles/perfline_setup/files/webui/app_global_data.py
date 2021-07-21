from flask import Flask
from plumbum import local

from core import task_cache
from core.async.async_worker import AsyncWorker
exec(open('./../perfline.conf').read())

hostname = local["hostname"]["-s"]().strip()
app = Flask(__name__)
cache = task_cache.TaskCache()
async_worker = AsyncWorker()
report_resource_map = dict()

all_artif_dirs = ARTIFACTS_DIRS + BACKUP_ARTIFACTS_DIRS
