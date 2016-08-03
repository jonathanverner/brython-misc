from fabric.api import task, run, local
import os

import subprocess
import repos
import users
import groups

from server.lib.settings import settings
conf = settings(__package__,strip_leading=1)

@task
def run():
    local(' docker run --name gitolite -d -v $PWD/data/repos:/data -p 127.0.0.1:2222:22 derektamsen/gitserver')
    
@task
def init():
    # For first time setup
    key=open(conf.public_key_file,'r').read()
    local('GITSERVER_SSH_KEY="'+key+'" GITSERVER_SSH_ADMIN='+conf.gitolite_admin+' docker run --name gitolite -d -v $PWD/data/repos:/data -p 127.0.0.1:2222:22 derektamsen/gitserver')

@task
def shell():
    local('docker exec -t -i gitolite /bin/bash')

@task
def commit():
    subprocess.check_call(["git", "commit", "-a", "-m", "Committing changes via fabric"], cwd=os.path.join(os.getcwd(),conf.gitolite_path))