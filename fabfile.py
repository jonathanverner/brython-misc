#!/usr/bin/env python
# -*- coding:utf-8 -*-

from management import git, server, client

git.settings['gitolite_path']='./data/gitolite-admin/'
client.settings = {
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
    'css_files':[]
}
