#!/usr/bin/env python
# -*- coding:utf-8 -*-

# NOTE: How about using dulwich?

import os

class repo(object):
    def __init__(self, path, repo_name, clone_url=None, bare=True):
        """Creates a new repository in the directory @path/@repo_name.
           If @clone_url is not None, it creates it by cloning it
           from @clone_url. Otherwise it initializes a new repo.
           The repository will be bare if @bare is True."""

        self.workdir = os.path.join(path,repo_name)
        pass

    def commit(self,stage_all=False,commit_message='',branch='master'):
        """If @stage_all is False, commits staged changes to the branch @branch
           otherwise stages all changes in the working tree and commits them. """
        pass

    def diff(self):
        """Returns the diff of the commited branch vs. staged changes """
        pass

    def add(self,path):
        """equivalent of git add """
        pass

    def mv(self,origin,dest):
        """equivalent of git mv @origin @dest """
        pass

    def absolute_path(self, relative_path):
        return os.path.join(self.workdir,relative_path)

    def create_path(self, relative_path, node_type, attrs):
        if os.path.exists(self.absolute_path(relative_path)):
                return False
        if node_type == 'file':
            content = attrs.get('content','')
            open(self.absolute_path(relative_path),'w').write(content)
            os.chmod(self.absolute_path(relative_path),attrs.get('mode',0664))
            self.add(relative_path)
        elif node_type == 'dir':
            os.mkdir(self.absolute_path(relative_path),mode=attrs.get('mode',0777))
            # Git ignores empty directories
            self.create_path(os.path.join(relative_path,'.git_empty_dir'),node_type='file')

    def lsR(self,pattern='.*'):
        """Lists all paths present in repo matching the given regexp pattern @pattern """
        pass
