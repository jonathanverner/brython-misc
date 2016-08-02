from fabric.api import task, run, local
import os

import subprocess
import repos
import users
import groups

from server.lib.settings import SettingsFactory
conf = SettingsFactory.get_settings(__package__,strip_leading=1)

@task
def run():
    local('docker run -d -v $PWD/data/repos:/data -p 127.0.0.1:2222:22 derektamsen/gitserver')

@task
def commit():
    subprocess.check_call(["git", "commit", "-a", "-m", "Committing changes via fabric"], cwd=os.path.join(os.getcwd(),conf.gitolite_path))