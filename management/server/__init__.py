from fabric.api import task, local
from management import venv

import pip


@task
def serve():
    venv(['python3','server.py'])