from server.tests import settings
from server.lib.shell import ls
from sh import mkdir, touch, rm

import os

tdir = os.path.join(settings['temp_dir'],'.-.mtest')

def setup_function(f):
    rm('-rf',tdir)
    mkdir('-p',tdir)

def teardown_function(f):
    rm('-rf',os.path.join(settings['temp_dir'],'mtest'))

def test_ls():
    mkdir('-p',os.path.join(tdir,'a/b/c'))
    mkdir('-p',os.path.join(tdir,'a/c/d'))
    mkdir('-p',os.path.join(tdir,'a/d/e'))
    mkdir('-p',os.path.join(tdir,'b/c'))
    touch(os.path.join(tdir,'b/c/fd'))
    touch(os.path.join(tdir,'b/fdel'))
    lst = ls(tdir)
    assert set(lst) == set(['a/','b/'])
    lst = ls(tdir,pattern='^a/?$')
    assert set(lst) == set(['a/'])
    lst = ls(tdir,pattern='^[ab]*$')
    assert set(lst) == set(['a/','b/'])
    lst = ls(tdir,pattern='^[a/b]*$',recursive=True)
    assert set(lst) == set(['a/','b/','a/b/'])
    lst = ls(tdir,pattern='^[abcfd/]*$',recursive=True)
    assert set(lst) == set(['a/','b/','a/b/','a/b/c/','a/c/','a/c/d/','a/d/','b/c/','b/c/fd'])

