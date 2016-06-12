from lib.RPCClient import RPCClientFactory
from lib.angular.core import Service
from lib.async import interruptible, interruptible_init, async_class, Return
from lib.events import EventMixin

from lib.logger import Logger
logger = Logger(__name__)


class User(EventMixin):

    def __init__(self,svc,data):
        super(User,self).__init__()
        self._svc = svc
        for (k,v) in data.items():
            setattr(self,k,v)


@async_class
class UserService(Service):

    @interruptible_init
    def __init__(self):
        super(UserService,self).__init__()
        logger.debug("Initializing User Service")
        self.user = None
        self._rpc = yield RPCClientFactory.get_client('user')
        self.user = yield self._rpc.get_profile()

    @interruptible
    def login(self,username,password):
        try:
            logger.debug("Logging in with",username, password)
            self.user = yield self._rpc.login(username,password)
            yield Return(True)
        except Exception as ex:
            logger.warn("Exception when logging in:", ex)
            yield Return(False)







