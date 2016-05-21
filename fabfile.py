#!/usr/bin/env python
# -*- coding:utf-8 -*-

from fabric.api import task, run, local
from management.shell import cp, cpR, cat, stream, ls
import os, sys

try:
    from scss import Scss
    sass = Scss().compile
except:
    sass = "sass --scss"

sass_files = ["./client/sass/base.scss","./client/sass/widgets.scss"]
css_files = [""]

#def compile_js(src,dst=None):
    #if dst is not None:
        ##stream("browserify "+src,program=True).pipe("babel --presets es2015").save(dst)
        ##stream("browserify -t babelify --presets es2015 "+src,program=True).save(dst)
        #stream("browserify "+src,program=True).save(dst)
    #else:
        ##return stream("browserify "+src,program=True).pipe("babel --presets es2015")
        ##return stream("browserify -t babelify --presets es2015 "+src,program=True)
        #return stream("browserify "+src,program=True)



import jinja2
from jinja2.filters import environmentfilter
jinja_env=jinja2.Environment(extensions=['jinja2.ext.autoescape'])
jinja_env.loader=jinja2.FileSystemLoader(["."])
def render_tpl(tpl,context,dst):
    stream(jinja_env.get_template(tpl).render(context)).save(dst)


@task
def stylesheets(target_dir='./client/assets/css'):
    css_stream = cat(css_files)
    for s in sass_files:
        css_stream.append(cat(s).pipe(sass,cwd=os.path.dirname(s)))
    css_stream.pipe("uglifycss").save(os.path.join(target_dir,"base.css"))

@task
def compile():
    stylesheets()