#!/usr/bin/env python
# -*- coding:utf-8 -*-

from sh import rm

from tornado.gen import coroutine, Return
from tornado.concurrent import run_on_executor, futures
from tornado import ioloop

from ..lib.tornado import RPCService, export
from ..lib.auth import logged_in, auth, AuthMixin
from ..lib import update_params

from ..lib.decorator import decorator
from ..lib.git import repo
from ..lib.gitolite import Gitolite
from ..lib.settings import settings
from ..lib.shell import ls

import os,re

conf = settings('project')
conf.default({
        'workdirs':'/tmp/wd',
        'gitolite_wd':'data/gitolite-admin',
        'gitolite_url':'ssh://git@localhost:2222',
})

class ProjectFactory:
    _projects = {}

    @classmethod
    def _full_id(cls,id,branch):
        return id+'-'+branch

    @classmethod
    def repo_url(cls,project_id):
        return conf.gitolite_url+'/'+project_id

    def __init__(self,api):
        self.io_loop = ioloop.IOLoop.current()
        self.executor = futures.ThreadPoolExecutor(8)
        self.api = api
        self.gitolite = Gitolite(conf.gitolite_wd,self.repo_url('gitolite-admin'))


    def get_project_for_user(self, project_id, branch, user):
        proj = self._projects.get(self._full_id(project_id,branch),None)
        if proj is None or user not in proj._users:
            return None
        return proj

    @coroutine
    def open_project(self,project_id,branch,user):
        meta = yield self.api.store.get("projects",project_id)
        if meta is None:
            raise Exception("No such project: " + str(project_id))
        meta['id'] = project_id
        proj_wd = os.path.join(conf.workdirs,project_id)
        if not os.path.isdir(proj_wd):
            os.mkdir(proj_wd)
        project = Project(meta,branch)
        project.add_user(user)
        self._projects[project.full_id()]=project
        return project

    @run_on_executor
    def close_project(self,project):
        del self._projects[project.full_id()]
        project._remove_workdir()



    @run_on_executor
    def create_project(self,meta,user):
        proj=self.api.store.create('projects')
        update_params(proj,meta,['title','repo_url'])
        proj['owner']=user
        if 'repo_url' not in meta:
            self.gitolite.create_repo(proj['id'])
            self.gitolite.add_rule(proj['id'],'RW+',[user])
            self.gitolite.save
            meta['repo_url'] = self.repo_url(proj['id'])
        self.api.store.save('project',proj)



class Project(object):
    def _ospath(self,path):
        real_path = os.path.realpath(os.path.join(self._wd,path))
        if not os.path.commonprefix([self._wd,real_path])==self._wd:
            raise Exception("Invalid path "+path)
        return real_path

    @classmethod
    def _create_node(cls,node_type,name):
        return {
            'type':node_type,
            'name':name,
            'children':{}
        }
    @classmethod
    def _build_tree(cls,flatlist):
        root = cls._create_node('dir','/')
        for item in flatlist:
            if item[0] != os.path.sep:
                item = os.path.sep + item
            items=item.split(os.path.sep)
            cur_dir=root
            for d in items[1:-1]:
                if d not in cur_dir['children']:
                    cur_dir['children'][d]=cls._create_node('dir',d)
                cur_dir = cur_dir['children'][d]
            if items[-1] != '':
                cur_dir['children'][items[-1]]=cls._create_node('file',items[-1])
        return root


    def __init__(self, meta_data, branch='master'):
        self.io_loop = ioloop.IOLoop.current()
        self.executor = futures.ThreadPoolExecutor(8)
        self.meta = meta_data
        self.branch = branch
        self._users = set()
        self._id = self.meta['id']
        self._full_id = ProjectFactory._full_id(self.meta['id'],branch)
        self._repo = repo(os.path.join(conf.workdirs,self._id),self.branch,clone_url=self.meta['repo_url'],branch=self.branch)
        self._wd = os.path.join(conf.workdirs,self._id,self.branch)

    def __repr__(self):
        return "Project("+self.full_id()+"):"+str(self.meta)+", wd:"+self._wd

    def full_id(self):
        return self._full_id

    @run_on_executor
    def _remove_workdir(self):
        rm('-rf',self._wd)

    @run_on_executor
    def read(self,path,revision=None):
        if revision is not None and revision != 'WORKDIR':
            if revision == 'STAGED':
                revision = ''
            return self._repo.read(path,revision)
        return open(self._ospath(path),'r').read()

    @run_on_executor
    def stage(self,path):
        self._repo.stage(path)

    @run_on_executor
    def commit(self,message):
        self._repo.commit(message)

    @run_on_executor
    def push(self):
        self._repo.push(branch=self.branch)

    @run_on_executor
    def pull(self):
        self._repo.pull(branch=self.branch)



    @run_on_executor
    def write(self,path,data):
        return open(self._ospath(path),'w').write(data)

    @run_on_executor
    def create(self,path):
        open(self._ospath(path),'w').close()

    @run_on_executor
    def mkdir(self,path):
        os.mkdir(self._ospath(path))

    @run_on_executor
    def rmdir(self,path):
        os.remove(self._ospath(path))

    @run_on_executor
    def mv(self,path_from,path_to):
        self._repo.mv(path_from,path_to)

    @run_on_executor
    def rm(self,path,force=True):
        self._repo.rm(path,force=force)

    @run_on_executor
    def query(self,pattern="WORKDIR:^(?!.git).*"):
        area,pattern = pattern.split(':',maxsplit=1)
        if area == 'STAGED':
            flatlist = self._repo.ls_staged()
        elif area == 'UNSTAGED':
            flatlist = self._repo.ls_unstaged()
        elif area == 'WORKDIR':
            return self._build_tree(ls(self._wd,pattern,recursive=True))
        else:
            flatlist = self._repo.ls_tree(area)
        pattern = re.compile(pattern)
        return self._build_tree([p for p in flatlist if pattern.match(p)])

    def add_user(self,user):
        self._users.add(user)

    def remove_user(self,user):
        self._users.remove(user)



@decorator
def project_opened(f):
    def decorated(self,*args,**kwargs):
        id = kwargs.get('project_id',None)
        branch = kwargs.get('branch','master')
        if id is None:
            raise Exception('Need to specify a project')
        project = self.factory.get_project_for_user(id,branch,self._api.session.user)
        if project is None:
            raise Exception('Project not opened: ', id, '('+branch+')')
        del kwargs['project_id']
        del kwargs['branch']
        return f(self,project,*args,**kwargs)
    return decorated


class ProjectService(RPCService,AuthMixin):
    SERVICE_NAME = 'project'
    auth_scope = 'projects'

    def __init__(self, server_api):
        super().__init__(server_api)
        self.factory = ProjectFactory(self._api)

    @export
    def open(self, project_id, branch='master'):
        project = self.factory.open_project(project_id,branch,self._api.session.user)
        raise Return(project)

    @export
    def create(self,data):
        raise Return(self.factory.create_project(data, self._api.session.user))


    @export
    @project_opened
    def close_project(self, project):
        project.remove_user(self._api.session.user)
        if len(project._users) == 0:
            self.factory.close_project(project)

    @export
    @project_opened
    def commit(self, project, message=''):
        raise Return(project.commit(message=message))

    @export
    @project_opened
    def stage(self, project, path):
        raise Return(project.stage(path))

    @export
    @project_opened
    def mkdir(self, project, path):
        raise Return(project.mkdir(path))

    @export
    @project_opened
    def write(self, project, path, contents):
        raise Return(project.write(path,contents))

    @export
    @project_opened
    def read(self, project, path):
        raise Return(project.read(path))

    @export
    @project_opened
    def mv(self, project, path_from, path_to):
        raise Return(project.mv(path_from,path_to))

    @export
    @project_opened
    def rm(self, project, path, force=True):
        raise Return(project.rm(path,force=force))


    @export
    @project_opened
    def query(self, project, pattern="WORKDIR:^(?!.git).*$"):
        raise Return(project.query(pattern = pattern))

services = [ProjectService]