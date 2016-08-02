import os
from fabric.api import task
from management.shell import cat
from server.lib.settings import settings, SettingsFactory

conf = SettingsFactory.get_settings(__package__,strip_leading=1)

try:
    from scss import Scss
    sass = Scss().compile
except:
    sass = "sass --scss"

@task
def build(target_dir=conf.css_asset_dir):
    css_stream = cat(conf.css_files)
    for s in conf.sass_files:
        css_stream.append(cat(s).pipe(sass,cwd=os.path.dirname(s)))
    css_stream.pipe("uglifycss").save(os.path.join(target_dir,"base.css"))