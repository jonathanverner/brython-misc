# Virtualenv

  --  Activate virtual_env `. venv.sh`
  --  Install packages `fab.server.pip install:package_name`

# Server

  --  Gitolite server (for serving repos) `fab git.run` (needs docker)
  --  Application server `fab server.serve` (based on tornado)

# Client

  --  Compile & copy everything `fab client.deploy.deploy`
  --  Note: for sass compilation new sass is needed (due to mdi),
      currently this is provided by a hackish shells script which
      enters the virtual_env and uses python's interface to libsass
      to compile the sass files

# Testing

  --  Run all tests `fab server.test.all`
  --  Cleanup after tests (delete repos, etc.) `fab server.test.cleanup`

# Other

  -- list fabric tasks `fab --list`

# Config

  -- Management: `fabfile.py`
  -- Server:
     -- Included plugins: `server/app.py`
     -- Configuration: use method `update_settings` from server.lib.settings
        (see `fabfile.py`) with appropriate scope (typically `server.plugins.project`
        for the `project` plugin. In code include
``
        from server.lib.settings import settings
        conf = settings(__package__)
``
        and then you can access setting keys as `conf.setting_key`.
