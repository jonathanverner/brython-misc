#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado.gen import coroutine,Return
from ..lib import EndpointHandler, event, update_params
from ..lib.auth import logged_in, auth, AuthMixin
import lib.git as git

import os


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


class ProjectsEndpoint(EndpointHandler,AuthMixin):
    open_projects = {}
    auth_scope = 'projects'
    _setting_scope = 'projects'

    default_settings = {
        'workdirs_location':'/tmp/wd',
        'repos_dir':'/tmp/repos'
    }

    @classmethod
    def _sanitize_git_url(cls,url,reject_local=True):
        #TODO: Needs a proper impImplementation
        return url

    def _get_open_project(self, project_id):
        proj = self.open_projects.get(project_id,None)
        if proj is None or self.user not in proj.users:
            return None
        return proj

    @event('open project')
    @coroutine
    @auth('open project')
    @logged_in #FIXME: Should allow anonymous users, but need to keep track of them in 'users'
    def open_project(self, project_id):
        if self.authorized('open',project_id):
            if project_id in self.open_projects:
                self.open_projects.users[self.user] = True
                raise Return(self.open_projects[project_id])
            else:
                project = self.store.get(project_id)
                repo = yield git.repo(self.get_setting('workdirs_location'), repo_name=project['id'],clone_url=project['git_url'], branch=project['branch'])
                self.open_projects[project_id] = {
                    'project':project,
                    'repo':repo,
                    'users':{self.user:True},
                    'workdir':os.path.join(self.get_setting('workdirs_location'),project['id']),
                }
            raise Return(self.open_projects[project_id])
        else:
            raise Return(self.error('Unauthorized'))

    @event('create project')
    @coroutine
    @auth('create project')
    def create_project(self,data):
        project = {
            'owner':self.user.id,
            'branch':'master',
        }
        update_params(project,data,['name','description','type'])
        project,repo = yield [
            self.store.save(data),
            git.repo(self.get_setting('repos_dir'),repo_name=project['id'], bare=True)
        ]
        raise Return(project)

    @event('clone project')
    @coroutine
    @logged_in
    def import_project(self,data):
        pass

    @event('close project')
    @project_opened
    def close_project(self, project):
        del project.users[self.user]
        if len(project.users) == 0:
            pass
            # TODO: Do seome garbage collection?

    @event('commit project')
    @coroutine
    @project_opened
    def commit_project(self, project, stage_all=False,message=''):
        yield project.repo.commit(stage_all=stage_all,commit_message=message)
        raise Return(self.success('Commit successful'))

    @event('stage change')
    @coroutine
    @project_opened
    @logged_in
    def stage_change(self, project, diff):
        yield project.repo.stage(diff=diff)
        raise Return(self.success('Change staged'))

    @event('get staged changes')
    @coroutine
    @project_opened
    @logged_in
    def staged_changes(self, project):
        diff = yield project.repo.diff()
        raise Return(diff)

    @event('create path')
    @coroutine
    @logged_in
    @project_opened
    def create_path(self, project, path, attrs):
        node_type = attrs.get('type','file')
        if project.repo.create_path(path,node_type,attrs):
            raise Return(self.success('Path created'))
        else:
            raise Return(self.error('Path exists'))

    @event('update path')
    @coroutine
    @logged_in
    @project_opened
    def update_path(self, project, path, path_info):
        if 'path' in path_info:
            project.repo.mv(path,path_info['path'])
        if 'mode' in path_info:
            os.chmod(project.repo.absolute_path(path),path_info['mode'])

    @event('query project')
    @coroutine
    @logged_in
    @project_opened
    def query_project(self, project, pattern):
        yield project.repo.lsR(pattern = pattern)

    @event('query projects')
    @coroutine
    @logged_in
    def query_project(self, query):
        yield self.store.get('projects',query)

endpoints = [('/projects',ProjectsEndpoint)]