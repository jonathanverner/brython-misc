from fabric.api import task
from management.venv import venv
from server.lib.settings import settings
import subprocess, os

conf = settings(__package__,strip_leading=1)

@task
def all():
    cleanup()
    venv(['python','-m', 'pytest', '--pdb','server'])
    cleanup()

@task
def single(test):
    cleanup()
    venv(['python','-m', 'pytest', '--pdb',test])
    cleanup()

@task
def cleanup():
    for repo in conf.test_repos:
        subprocess.check_call(["sudo","rm", "-rf", os.path.join(conf.repo_dir,repo)+".git"], cwd=os.getcwd())