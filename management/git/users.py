from fabric.api import task, local
from server.lib.gitolite import Gitolite
import os

from server.lib.settings import settings
conf = settings(__package__,strip_leading=1)

@task
def list():
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    print(' '.join(g.users()))

@task
def add(name,key):
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    g.add_user(name,key)
    g.save()

@task
def info(name):
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    groups = g.get_user_groups(name)
    key = g.get_user_key(name)
    print("Groups:", groups)
    print("Key:", key)

@task
def remove(name):
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    g.remove_user(name)
    g.save()

