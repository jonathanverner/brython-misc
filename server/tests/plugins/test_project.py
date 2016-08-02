from unittest.mock import patch
from server.tests import settings as test_settings
from server.tests.git_utils import create_test_repos, remove_test_repos, test_file, test_contents
import os, re
from sh import rm

from server.lib.gitolite import Gitolite

from tornado.gen import coroutine
from tornado.testing import AsyncTestCase, gen_test
from tornado.ioloop import IOLoop


from server.plugins.project import Project, ProjectFactory, ProjectService
from server.lib.tornado import RPCSvcApi, RPCServer
from server.lib.settings import update_settings

wds = os.path.join(test_settings['temp_dir'],'.-.wd')
update_settings(scope='project',keys={
    'workdirs':wds,
})

def setup_module(module):
    remove_test_repos()
    rm('-rf',wds)

def teardown_module(module):
    remove_test_repos()
    rm('-rf',wds)

def test_tree_dict_to_list():
    dict_tree = { 'name':'/', 'type':'dir', 'children':{
        'a':{'name':'a','type':'file','children':{}},
        'b':{'name':'b','type':'dir','children': {
            'c':{'name':'c','type':'file','children':{}},
            'd':{'name':'d','type':'dir','children':{}}
            }}
        }
    }
    list_tree = { 'name':'/', 'type':'dir', 'children':[
        {'name':'a','type':'file','children':[]},
        {'name':'b','type':'dir','children':
                 [{'name':'c','type':'file','children':[]},{'name':'d','type':'dir','children':[]}]}]
    }
    lst= Project.tree_dict_to_list(dict_tree)
    assert lst==list_tree


def test_build_tree():
    tree = Project._build_tree(['/a/','/b/','/a/b/','/a/b/c/','/d/e','/c'])
    assert tree == {'name':'/','type':'dir',
                    'children':{
                        'a':{'name':'a','type':'dir',
                             'children':{
                                 'b':{'name':'b','type':'dir',
                                      'children':{
                                          'c':{'name':'c','type':'dir',
                                               'children':{}
                                          }}
                                 }}
                        },
                        'b':{'name':'b','type':'dir',
                             'children':{}
                        },
                        'd':{'name':'d','type':'dir',
                             'children':{
                                 'e':{'name':'e','type':'file',
                                      'children':{}
                                 }}
                        },
                        'c':{'name':'c','type':'file',
                             'children':{}
                        }
        }
    }

class StoreMock(object):
    @coroutine
    def get(self,scope,id):
        return {
            'title':'Gitolite Admin',
            'owner':'admin',
            'repo_url':'ssh://git@localhost:2222/test_repo'+id
        }

class RPCServerMock(RPCServer):
    def __init__(self,*args,**kwargs):
        self.store = StoreMock()


class ApiMock(RPCSvcApi):
    def __init__(self,server,svc):
        self.svc = svc
        self.server = RPCServerMock()

@patch('server.lib.gitolite.Gitolite')
@patch('server.lib.tornado.RPCSvcApi',ApiMock)
class TestProjectFactory(AsyncTestCase):

    @classmethod
    def setUpClass(cls):
        create_test_repos(['test_repoA','test_repoB','test_repoC'])

    @classmethod
    def tearDownClass(cls):
        remove_test_repos()

    def setup_method(self,method):
        if not os.path.isdir(wds):
            os.mkdir(wds)

    def teardown_method(self,method):
        rm('-rf',wds)

    @gen_test
    def test_init(self,gitolite,*args):
        a = ApiMock(None,'Mock Service')
        factory = ProjectFactory(a)

    @gen_test
    def test_open_project(self,gitolite,*args):
        a = ApiMock(None,'Mock Service')
        factory = ProjectFactory(a)
        proj = yield factory.open_project('A','master','admin')
        self.assertIsInstance(proj,Project)

    @gen_test
    def test_project_actions(self,gitolite,*args):
        a = ApiMock(None,'Mock Service')
        factory = ProjectFactory(a)
        proj = yield factory.open_project('B','master','admin')
        c = yield proj.read(test_file)
        c = yield proj.read(test_file); assert c  == test_contents
        yield proj.write(test_file,'New contents')
        c = yield proj.read(test_file,revision='STAGED'); assert c  == test_contents
        c = yield proj.read(test_file,revision='HEAD'); assert c  == test_contents
        c = yield proj.read(test_file); assert c  == 'New contents'
        yield proj.stage(test_file)
        c = yield proj.read(test_file); assert c  == 'New contents'
        c = yield proj.read(test_file,revision='STAGED'); assert c  == 'New contents'
        c = yield proj.read(test_file,revision='HEAD'); assert c  == test_contents
        yield proj.commit("Test commit")
        c = yield proj.read(test_file); assert c  == 'New contents'
        c = yield proj.read(test_file,revision='STAGED'); assert c  == 'New contents'
        c = yield proj.read(test_file,revision='HEAD'); assert c  == 'New contents'
        yield proj.rm(test_file)
        yield proj.commit("Deleting: "+test_file)
        yield proj.push()

    @gen_test
    def test_project_query(self,gitolite,*args):
        a = ApiMock(None,'Mock Service')
        factory = ProjectFactory(a)
        proj = yield factory.open_project('C','master','admin')
        yield proj.rm('README.md')
        yield proj.commit('Delete README.md')
        yield proj.write('A','file A:1')
        yield proj.write('B','file B:1')
        yield proj.mkdir('dir')
        lst = yield proj.query('WORKDIR:^(?!.git).*')
        assert lst == {
            'name':'/',
            'type':'dir',
            'children': { 'A':{'name':'A','type':'file','children':{} },
                          'B':{'name':'B','type':'file','children':{} },
                          'dir':{'name':'dir','type':'dir','children':{} }}
        }, "Test listing of the contents of working directory (should include empty directories)"

        lst = yield proj.query('STAGED:.*')
        assert lst == { 'name':'/', 'type':'dir', 'children':{} }, "Test listing of the (empty) staging area"
        lst = yield proj.query('HEAD:.*')
        assert lst == { 'name':'/', 'type':'dir', 'children':{} }, "Test listing of the (empty) HEAD"
        lst = yield proj.query('UNSTAGED:.*')
        assert lst == {
            'name':'/',
            'type':'dir',
            'children':{  'A':{'name':'A','type':'file','children':{} },
                          'B':{'name':'B','type':'file','children':{} }
                       }
        }, "Test listing of changes relative to staging area (includes untracked but not empty directories)"
        yield proj.write('dir/C','file dir/C:1')
        lst = yield proj.query('UNSTAGED:.*')
        assert lst == {
            'name':'/',
            'type':'dir',
            'children':{  'A':{'name':'A','type':'file','children':{} },
                          'B':{'name':'B','type':'file','children':{} },
                          'dir':{'name':'dir','type':'dir','children':{'C':{'name':'C','type':'file','children':{}}}}
                       }
        }, "Test listing of changes relative to staging area"
        yield proj.stage('A')
        lst = yield proj.query('STAGED:.*')
        assert lst == { 'name':'/', 'type':'dir', 'children':{'A':{'name':'A','type':'file','children':{} }} }, "Test listing of the staging area (should include staged file A)"
        lst = yield proj.query('UNSTAGED:.*')
        assert lst == {
            'name':'/',
            'type':'dir',
            'children':{  'B':{'name':'B','type':'file','children':{} },
                          'dir':{'name':'dir','type':'dir','children':{'C':{'name':'C','type':'file','children':{}}}}
                       }
        }, "Test listing of changes relative to staging area (should exclude staged file A)"
        yield proj.write('A','file A:2')
        lst = yield proj.query('UNSTAGED:.*')
        assert lst == {
            'name':'/',
            'type':'dir',
            'children':{  'A':{'name':'A','type':'file','children':{} },
                          'B':{'name':'B','type':'file','children':{} },
                          'dir':{'name':'dir','type':'dir','children':{'C':{'name':'C','type':'file','children':{}}}}
                       }
        }, "Test listing of changes relative to staging area (includes a staged file with unstaged changes A)"
        yield proj.commit('Commit changes to A')
        lst = yield proj.query('STAGED:.*')
        assert lst == { 'name':'/', 'type':'dir', 'children':{} }, "Test listing of the staging area (empty after commit)"
        lst = yield proj.query('HEAD:.*')
        assert lst == { 'name':'/', 'type':'dir', 'children':{'A':{'name':'A','type':'file','children':{} }} }, "Test listing of HEAD revision (should include commited file A)"
        yield proj.rm('A')
        yield proj.rm('B')
        yield proj.rm('dir/C')
        yield proj.commit("Commiting test changes")
        yield proj.push()

