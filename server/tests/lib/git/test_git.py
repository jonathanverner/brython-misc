from server.lib.git import repo
from server.tests import settings
import os,subprocess

tmp = settings['temp_dir']

def test_clone():
    r = repo(tmp,'test-repo',clone_url='ssh://git@localhost:2222/gitolite-admin')
    assert os.path.isdir(os.path.join(tmp,'test-repo'))
    assert os.path.isdir(os.path.join(tmp,'test-repo/.git'))

def test_clone_bare():
    r = repo(tmp,'test-repo',clone_url='ssh://git@localhost:2222/gitolite-admin',bare=True)
    assert os.path.isdir(os.path.join(tmp,'test-repo'))
    assert os.path.isfile(os.path.join(tmp,'test-repo/config'))

def test_init_repo():
    r = repo(tmp,'test-repo')
    assert os.path.isdir(os.path.join(tmp,'test-repo'))
    assert os.path.isfile(os.path.join(tmp,'test-repo/.git/config'))

def test_existing_repo():
    r = repo(tmp,'test-repo',clone_url='ssh://git@localhost:2222/gitolite-admin')
    r2 = repo(tmp,'test-repo')
    assert r2._remote == 'ssh://git@localhost:2222/gitolite-admin'

def test_ls_repo():
    r = repo(tmp,'test-repo')
    a = open(os.path.join(tmp,'test-repo/a'),'w')
    a.write('ahoj')
    a.close()
    assert len(r.ls_staged()) == 0
    assert r.ls_unstaged() == ['a']
    assert r.ls_unstaged(include_untracked=False) == []
    r.stage('a')
    assert r.ls_staged() == ['a']
    assert r.ls_unstaged() == []
    r.commit(commit_message='MSG')
    a = open(os.path.join(tmp,'test-repo/a'),'w')
    a.write('cau')
    assert r.ls_unstaged() == ['a']
    assert r.ls_unstaged(include_untracked=False) == ['a']

def test_ls_tree_repo():
    r = repo(tmp,'test-repo')
    a = open(os.path.join(tmp,'test-repo/a'),'w')
    a.write('ahoj')
    a.close()
    r.stage('a')
    r.commit(commit_message='MSG')
    r.rm('a')
    r.commit(commit_message='MSG')
    assert r.ls_tree() == []
    a = open(os.path.join(tmp,'test-repo/a'),'w')
    a.write('ahoj')
    a.close()
    r.stage('a')
    r.commit(commit_message='MSG')
    assert r.ls_tree() == ['a']
    os.mkdir(os.path.join(tmp,'test-repo/b'))
    c = open(os.path.join(tmp,'test-repo/b/c'),'w')
    c.write('cau')
    c.close()
    r.stage('b/c')
    r.commit(commit_message='MSG')
    assert sorted(r.ls_tree()) == sorted(['a','b/c'])
    assert sorted(r.ls_tree(tree='HEAD^')) == sorted(['a'])

def test_read_repo():
    r = repo(tmp,'test-repo')
    a = open(os.path.join(tmp,'test-repo/a'),'w')
    a.write('ahoj')
    a.close()
    r.stage('a')
    r.commit(commit_message='MSG')
    assert r.read('a') == 'ahoj'
    a = open(os.path.join(tmp,'test-repo/a'),'w')
    a.write('cau')
    a.close()
    r.stage('a')
    r.commit(commit_message='MSG')
    assert r.read('a') == 'cau'
    assert r.read('a',revision='HEAD^') == 'ahoj'

def teardown_function(function):
    subprocess.check_call(["rm", "-rf", "/tmp/test-repo"])