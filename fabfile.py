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
        }
    },
    'sass_files': [ "./client/sass/base.scss",
                    "./client/sass/widgets.scss",
                    "./client/bower_components/sass-bootstrap-glyphicons/scss/bootstrap-glyphicons.scss"],
    'css_files':[],
    'css_asset_dir':'./client/assets/css'
},'client')

from management import git, server, client

