from fabric.api import task, local
from server.lib.gitolite import Gitolite
import os
from .settings import settings

@task
def list():
    g = Gitolite(os.path.join(os.getcwd(),settings['gitolite_path']))
    print(' '.join(g.users()))

@task
def add(name,key):
    g = Gitolite(os.path.join(os.getcwd(),settings['gitolite_path']))
    g.add_user(name,key)
    g.save()

@task
def info(name):
    g = Gitolite(os.path.join(os.getcwd(),settings['gitolite_path']))
    groups = g.get_user_groups(name)
    key = g.get_user_key(name)
    print("Groups:", groups)
    print("Key:", key)

@task
def remove(name):
    g = Gitolite(os.path.join(os.getcwd(),settings['gitolite_path']))
    g.remove_user(name)
    g.save()

