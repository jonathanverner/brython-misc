from fabric.api import task, local
from management.venv import venv
import subprocess,os

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
    subprocess.check_call(["sudo","rm", "-rf", "data/repos/git/repositories/test_repo.git"], cwd=os.getcwd())
    subprocess.check_call(["sudo","rm", "-rf", "data/repos/git/repositories/test_repoA.git"], cwd=os.getcwd())
    subprocess.check_call(["sudo","rm", "-rf", "data/repos/git/repositories/test_repoB.git"], cwd=os.getcwd())
    subprocess.check_call(["sudo","rm", "-rf", "data/repos/git/repositories/test_repoC.git"], cwd=os.getcwd())
    subprocess.check_call(["sudo","rm", "-rf", "data/repos/git/repositories/test_remote_repo.git"], cwd=os.getcwd())