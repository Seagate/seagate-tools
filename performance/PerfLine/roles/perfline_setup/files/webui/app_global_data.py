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

artifacts_dirs = [ARTIFACTS_DIR]
night_daemon_dirs = [NIGHT_ARTIFACTS]

if BACKUP_ARTIFACTS_DIR:
    backup_artifacts_dirs = [BACKUP_ARTIFACTS_DIR]
else:
    backup_artifacts_dirs = []

all_artif_dirs = artifacts_dirs + backup_artifacts_dirs
