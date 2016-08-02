from fabric.api import task, local
from management.venv import venv
import pip

@task
def install(package):
    venv(['pip','install',package])

@task
def list():
    venv(['pip','list'])

@task
def freeze():
    venv(['pip','freeze','> requirements.txt'])

@task
def uninstall(package):
    venv(['pip','uninstall',package])
