from fabric.api import task, local
from server.lib.gitolite import Gitolite
import os

from server.lib.settings import settings
conf = settings(__package__,strip_leading=1)

@task
def list():
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    print(' '.join(g.groups()))

@task
def add(name):
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    g.add_group(name)
    g.save()

@task
def info(name):
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    users = g.get_group(name)
    print("Users:", ' '.join(users))

@task
def remove(name):
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    g.remove_group(name)
    g.save()

@task
def add_user(group,name):
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    g.add_user_to_group(name,group)
    g.save()

@task
def remove_user(group,name):
    g = Gitolite(os.path.join(os.getcwd(),conf.gitolite_path))
    g.remove_user_from_group(name,group)
    g.save()


