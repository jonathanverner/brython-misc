from fabric.api import task
from management.venv import venv
from server.lib.settings import settings
import subprocess, os

conf = settings(__package__,strip_leading=1)

@task
def all():
    cleanup()
    venv(['python','-m', 'pytest', 'client/tests'])
    cleanup()

@task
def single(test):
    cleanup()
    venv(['python','-m', 'pytest', '--pdb','--full-trace', '--maxfail=1',os.path.join('client/tests',test)])
    cleanup()

@task
def cleanup():
    pass