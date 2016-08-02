from server.tests import settings as test_settings

import os
from sh import rm
from server.lib.gitolite import Gitolite
from server.lib.git import repo

wds = os.path.join(test_settings['temp_dir'],'.-.wd')


_test_repos = []
test_file='README.md'
test_contents='Empty repo'

def create_test_repos(repo_names,empty=False):
    if not os.path.isdir(wds):
        os.mkdir(wds)
    manager = Gitolite(path=os.path.join(wds,'gitolite-admin'),url=test_settings['gitolite_url'])
    for r in repo_names:
        manager.create_repo(r)
        manager.add_rule(r,'RW+',['@all'])
    manager.save()
    if not empty:
        for repo_name in repo_names:
            r = repo(wds,repo_name,clone_url='ssh://git@localhost:2222/'+repo_name,branch=None)
            readme=open(os.path.join(r._workdir,test_file),'w')
            readme.write(test_contents)
            readme.close()
            r.stage(test_file)
            r.commit("Initial commit")
            r.push()
    rm('-rf',wds)
    _test_repos.extend(repo_names)


def create_test_repo(repo_name,empty=False,ensure_new=True):
    if repo_name in _test_repos:
        if not ensure_new:
            return
        remove_test_repo(repo_name)
    if not os.path.isdir(wds):
        os.mkdir(wds)
    manager = Gitolite(path=os.path.join(wds,'gitolite-admin'),url=test_settings['gitolite_url'])
    manager.create_repo(repo_name)
    manager.add_rule(repo_name,'RW+',['@all'])
    manager.save()
    if not empty:
        r = repo(wds,repo_name,clone_url='ssh://git@localhost:2222/'+repo_name,branch=None)
        readme=open(os.path.join(r._workdir,test_file),'w')
        readme.write(test_contents)
        readme.close()
        r.stage(test_file)
        r.commit("Initial commit")
        r.push()
    rm('-rf',wds)
    _test_repos.append(repo_name)

def remove_test_repo(repo_name):
    if not repo_name in _test_repos:
        return
    if not os.path.isdir(wds):
        os.mkdir(wds)
    manager = Gitolite(path=os.path.join(wds,'gitolite-admin'),url=test_settings['gitolite_url'])
    manager.remove_repo(repo_name)
    manager.save()
    rm('-rf',wds)
    _test_repos.remove(repo_name)

def remove_test_repos():
    if len(_test_repos) == 0:
        return
    if not os.path.isdir(wds):
        os.mkdir(wds)
    manager = Gitolite(path=os.path.join(wds,'gitolite-admin'),url=test_settings['gitolite_url'])
    for repo in set(_test_repos):
        manager.remove_repo(repo)
    manager.save()
    rm('-rf',wds)
    _test_repos.clear()
