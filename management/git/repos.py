from fabric.api import task, local
from server.lib.gitolite import Gitolite
import os, subprocess
from server.lib.settings import SettingsFactory
conf = SettingsFactory.get_settings(__package__,strip_leading=1)

@task
def list():
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    print(' '.join(g.get_repos()))
    #local('ssh -p 2222 git@localhost')

@task
def create(name):
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    g.create_repo(name)
    g.save()

@task
def remove(name):
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    g.remove_repo(name)
    g.save()
    subprocess.check_call(["sudo","rm", "-rf", "data/repos/git/repositories/"+name+".git"], cwd=os.getcwd())

@task
def add_rule(name, rule):
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    g.add_rule_string(name,rule)
    g.save()


