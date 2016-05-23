from lib.RPCClient import RPCClientFactory
from lib.angular.core import Service, JSDict
import lib.angular.core as ngcore
from lib.async import interruptible, interruptible_init, async_class, Return
from lib.events import EventMixin

from lib.logger import Logger
logger = Logger(__name__)


class Project(EventMixin):

    def __init__(self,rpc,data):
        super(Project,self).__init__()
        self.rpc = rpc
        self.data = self.data
        self.files = []

    @interruptible
    def _load_files(self,path):
        self.files = yield self.query_files(self,"")

    def close(self):
        promise =  self.rpc.close_project(self.data.id)
        promise.bind('success',self,'closed')
        return promise

    def commit(self):
        return self.rpc.commit_project(self.data.id)

    def create_path(self, path):
        return self.rpc.create_path(path)

    def update_file(self,path,contents):
        return self.rpc.update_file(self.data.id,path,contents)

    def read_file(self,path):
        return self.rpc.get_file(self.data.id,path)

    def query_files(self,path):
        return self.rpc.query_file(self.data.id,path)

@async_class
class ProjectService(Service):

    @interruptible_init
    def __init__(self):
        super(ProjectService,self).__init__()
        self.project_list = []
        self.open_projects = []
        self._rpc_project = yield RPCClientFactory.get_client('project')
        self._rpc_projectfs = yield RPCClientFactory.get_client('projectfs')
        project_list = yield self._rpc_projectfs.query()
        self.project_list = [ ngcore.JSDict(p) for p in project_list ]

    @interruptible
    def open_project(self,project_id):
        project_data = yield self._rpc_project.open(project_id)
        project = Project(self._rpc_project,project_data)
        self.open_projects.append(project)
        project.bind('closed',self._close_project)
        yield project._load_files()
        yield Return(project)

    @interruptible
    def _close_project(self,event):
        proj = event.target
        self.open_projects.remove(proj)







