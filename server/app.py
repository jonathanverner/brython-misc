from importlib import import_module
import logging
import sys

from . import plugins
from .lib.tornado import RPCServer, RPCService
from .lib.storage import FileStore


class RPCEndpoint(RPCServer):
    settings = {}
    __urls__ = []

    @classmethod
    def load_plugin(cls,plugin_name):
        plugin = import_module(__package__+'.plugins.'+plugin_name)

        # Load endpoints defined by the plugin
        if hasattr(plugin,'services'):
            for service in plugin.services:
                if service.SERVICE_NAME in cls.REGISTERED_SERVICES:
                    print("Plugin", plugin_name, "overrides service", service.SERVICE_NAME, "(original handler:", cls.REGISTERED_SERVICES[service.SERVICE_NAME],")")
                cls.register_service(service)

        # Load url handlers defined by the plugin
        if hasattr(plugin,'urls'):
            for (regexp,handler) in plugin.urls:
                cls.__urls__.append(("/plugins/"+plugin_name+"/"+regexp,handler))

log = logging.getLogger("App")
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler(sys.stderr))

#plugins = ['infinote','project','user','chat','projectfs']
plugins = ['chat']
for p in plugins:
    log.info("Loading plugin: %s", p)
    RPCEndpoint.load_plugin(p)

RPCEndpoint.store = FileStore('db.json')

log.info("Registered Services: %s",RPCEndpoint.REGISTERED_SERVICES.keys())
log.info("Persistent Storage: %s",RPCEndpoint.store)