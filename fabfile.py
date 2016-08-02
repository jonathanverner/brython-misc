#!/usr/bin/env python
# -*- coding:utf-8 -*-

from server.lib.settings import update_settings

update_settings({
    'gitolite_path':'./data/gitolite-admin/'
},'git')

update_settings({
    'assets' : {
        'glyphicon-fonts': {
            'source':'./client/bower_components/sass-bootstrap-glyphicons/fonts/',
            'target':'./client/assets/fonts/',
            'pattern':'.*',
        },
        'material-icons': {
            'source':'./client/bower_components/mdi/fonts/',
            'target':'./client/assets/fonts/',
            'pattern':'.*',
        }
    },
    'sass_files': [ "./client/sass/base.scss",
                    "./client/sass/widgets.scss",
                    "./client/bower_components/mdi/scss/materialdesignicons.scss"],
    'css_files':[],
    'css_asset_dir':'./client/assets/css'
},'client')

update_settings({
    'repo_dir':'data/repos/git/repositories',
    'test_repos':['test_repo',
                  'test_repoA',
                  'test_repoB',
                  'test_repoC',
                  'test_remote_repo']
},'server')

from management import git, server, client

