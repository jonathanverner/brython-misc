from fabric.api import task, local
from management.venv import venv

@task
def all():
    venv(['python','-m', 'pytest', '--pdb','server'])