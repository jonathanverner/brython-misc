from fabric.api import task, local
from management.venv import venv

import pip
import test


@task
def serve():
    venv(['python3','server.py'])