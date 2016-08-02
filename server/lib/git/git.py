#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# NOTE: How about using dulwich?

from __future__ import absolute_import
import os, sys, re, json
from sh import git

class repo(object):
    REF_HEAD=0
    REF_STAGED=1
    REF_WORKTREE=2
    _STATUS_LINE_A_RE=re.compile('^(?P<stat_staged>[ MADRCU?!])(?P<stat_work>[ MADRCU?!])\s(?P<path_orig>.*)\s->\s(?P<path_new>.*)$')
    _STATUS_LINE_B_RE=re.compile('^(?P<stat_staged>[ MADRCU?!])(?P<stat_work>[ MADRCU?!])\s(?P<path_orig>.*)$')

    def __init__(self, path, repo_name, clone_url=None, branch="master", bare=False):
        """Creates a new repository in the directory @path/@repo_name.
           If @clone_url is not None, it creates it by cloning it
           from @clone_url. Otherwise it initializes a new repo.
           The repository will be bare if @bare is True."""

        self._workdir = os.path.join(path,repo_name)

        if not os.path.isdir(self._workdir):
            self._remote = clone_url
            if self._remote:
                if branch is not None:
                    git.clone("--branch", branch, self._remote, self._workdir, bare=bare)
                else:
                    git.clone(self._remote, self._workdir, bare=bare)
            else:
                git.init(self._workdir,bare=bare)
        else:
            if os.path.isfile(os.path.join(self._workdir,'.git/config')):
                cfg = os.path.join(self._workdir,'.git/config')
            else:
                cfg = os.path.join(self._workdir,'config')
            config = open(cfg).read()
            m = re.match('^.*\s*url\s*=\s*(?P<url>[^\s]*)\s.*$', config,re.IGNORECASE | re.DOTALL)
            if m:
                self._remote = m.groupdict()['url']
            else:
                self._remote = None
        self._git = git.bake(_cwd=self._workdir,_tty_out=False)

    def commit(self,commit_message):
        """Commits staged changes with the givven commit message """
        self._git.commit(message=commit_message)

    def pull(self):
        self._git.pull()

    def push(self):
        self._git.push()

    # Methods for dealing with the index (staging area)
    def stage(self, path):
        self._git.add(path)

    def unstage(self,path):
        """ Same as git reset path """
        self._git.reset(path)

    def stage_patch(self, patch):
        self._git.apply('--cached',"-",_in=patch)

    def mv(self,origin,dest):
        """equivalent of git mv @origin @dest """
        self._git("mv",origin, dest)

    def rm(self,path):
        self._git("rm",path)

    def status(self):
        ret = []
        for ln in self._git.status('-uall',porcelain=True).split('\n'):
            if ln == '':
                continue
            match = repo._STATUS_LINE_A_RE.match(ln)
            if not match:
                match = repo._STATUS_LINE_B_RE.match(ln)
            if not match:
                raise Exception("Unexpected line in git status output: '"+ln+"'")
            match = match.groupdict()
            if 'path_new' in match and match['path_new'][0]=='"':
                match['path_new'] = json.loads(match['path_new'])
            if match['path_orig'][0] == '"':
                match['path_orig'] = json.loads(match['path_orig'])
            ret.append(match)
        return ret

    def ls_staged(self):
        stat = self.status()
        ret = []
        for s in stat:
            if (not s['stat_staged'] == '?') and (not s['stat_staged'] == ' '):
                if 'path_new' in s:
                    ret.append(s['path_new'])
                else:
                    ret.append(s['path_orig'])
        return ret

    def ls_unstaged(self, include_untracked=True):
        stat = self.status()
        ret = []
        for s in stat:
            if (not s['stat_work'] == ' ' and not s['stat_work'] == '?') or (include_untracked and s['stat_work'] == '?'):
                if 'path_new' in s:
                    ret.append(s['path_new'])
                else:
                    ret.append(s['path_orig'])
        return ret

    def ls_tree(self,tree='HEAD'):
        return [ f for f in self._git('ls-tree','-r','--name-only',tree).split('\n') if f != '']

    def read(self,path,revision='HEAD'):
        return str(self._git.show('--no-color', revision+':'+path))


    def diff(self,source,target,path):
        """
            Returns the diff on @path between source and target.
            @source and @target can either be any commit or one of
            repo.REF_STAGED, repo.REF_WORKTREE.

            Note: The command assumes that @source comes before @target,
            and the special cases are ordered as follows:
                committed < staged < worktree
        """
        if source == repo.REF_STAGED:
            source = ""
        if target == repo.REF_WORKTREE:
            target = ""
        if target == repo.REF_STAGED:
            target = "--cached"
        return self._git.diff(source,target,path)