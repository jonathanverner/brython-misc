import os
from fabric.api import task
from management.shell import cat

from server.lib.settings import settings
conf = settings(__package__,strip_leading=1)

try:
    import sass
    sass = sass.compile
except Exception as e:
    sass=os.path.join(os.path.dirname(__file__),"sass.sh")

@task
def build(target_dir=conf.css_asset_dir):
    css_stream = cat(conf.css_files)
    for s in conf.sass_files:
        css_stream.append(cat(s).pipe(sass,cwd=os.path.dirname(s)))
    css_stream.pipe("uglifycss").save(os.path.join(target_dir,"base.css"))