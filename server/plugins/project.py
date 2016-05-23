#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado.gen import coroutine, Return
from ..lib.tornado import RPCService, export
from ..lib.auth import logged_in, auth, AuthMixin
from ..lib import update_params
from .lib import git

import os


class Project:
    def __init__(self, meta_data):
        self.meta = meta_data
        self._users = []
        pass

    def stage(self,diff=None):
        pass

    def commit(self,stage_all=False,commit_message=None):
        pass

    def create_dir(self,path):
        pass

    def update_file(self,path,contents):
        pass

    def read_file(self,path):
        return "Testing contents"

    def mv(self,path_from,path_to):
        pass

    def rm(self,path):
        pass

    def query(self,path=""):
        return ['test_file.txt','test_file.py']

    def add_user(self,user):
        pass

    def remove_user(self,user):
        pass



@decorator
def project_opened(f):
    def decorated(self,*args,**kwargs):
        id = kwargs.get('project_id',None)
        if id is None:
            return self.error('Need to specify a project')
        project = self._get_open_project(id)
        if project is None:
            return self.error('Project not opened')
        del kwargs['project_id']
        kwargs['project'] = project
        return f(self,*args,**kwargs)
    return decorated


class ProjectService(RPCService,AuthMixin):
    SERVICE_NAME = 'project'
    open_projects = {}
    auth_scope = 'projects'
    _setting_scope = 'projects'

    default_settings = {
        'workdirs_location':'/tmp/wd',
        'repos_dir':'/tmp/repos'
    }

    def _get_open_project(self, project_id):
        proj = self.open_projects.get(project_id,None)
        if proj is None or self.session.user not in proj._users:
            return None
        return proj

    @export
    @coroutine
    def open_project(self, project_id):
        if not project_id in self.open_projects:
            meta = yield self.store.get("projects",project_id)
            meta['project_id'] = project_id
            self.open_projects[project_id] = Project(meta)
        self.open_projects[project_id].add_user(self.session.user)
        raise Return(self.open_projects[project_id])

    @export
    @coroutine
    def create_project(self,data):
        meta = {
            "owner":self.session.user.id,
        }
        update_params(meta,data,['title'])
        project = Project(meta)
        project.add_user(self.session.user)
        raise Return(project)


    @export
    @project_opened
    def close_project(self, project):
        project.remove_user(self.session.user)
        if len(project._users) == 0:
            del self.open_projects[project.meta['id']]

    @export
    @coroutine
    @project_opened
    def commit_(self, project, stage_all=False, message=''):
        raise Return(project.commit(stage_all=stage_all,commit_message=message))

    @export
    @coroutine
    @project_opened
    def stage(self, project, diff=None):
        raise Return(project.stage(diff=diff))

    @export
    @coroutine
    @project_opened
    def create_dir(self, project, path, attrs):
        raise Return(project.create_dir(path))

    @export
    @coroutine
    @project_opened
    def update_file(self, project, path, contents):
        project.update_file(path,contents)

    @export
    @coroutine
    @project_opened
    def read_file(self, project, path):
        project.read_file(path)

    @export
    @coroutine
    @project_opened
    def mv(self, project, path_from, path_to):
        project.mv(path_from,path_to)

    @export
    @coroutine
    @project_opened
    def rm(self, project, path_from, path_to):
        project.mv(path_from,path_to)


    @export
    @coroutine
    @project_opened
    def query(self, project, pattern=""):
        raise Return(project.query(pattern = pattern))

services = [ProjectService]