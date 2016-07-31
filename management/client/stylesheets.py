import os
from fabric.api import task
from management.shell import cat

from .settings import settings

sass_files = settings['sass_files']
css_files = settings['css_files']


try:
    from scss import Scss
    sass = Scss().compile
except:
    sass = "sass --scss"

@task
def build(target_dir='./client/assets/css'):
    css_stream = cat(css_files)
    for s in sass_files:
        css_stream.append(cat(s).pipe(sass,cwd=os.path.dirname(s)))
    css_stream.pipe("uglifycss").save(os.path.join(target_dir,"base.css"))