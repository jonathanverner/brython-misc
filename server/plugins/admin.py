from ..lib.tornado import RPCService, export
from tornado.gen import coroutine

class AdminService(RPCService):
    SERVICE_NAME='admin'

    @coroutine
    @export
    def persists_storage(self):
        yield self._api.store.persist()

services = [AdminService]