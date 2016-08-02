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
        self.data = data.meta
        self.branch = data.branch

    @interruptible
    def _load_workdir(self):
        logger.log("Loading workdir files")
        root = yield self.query('WORKDIR:^(?!.git).*$')
        self.workdir = root.children
        logger.log(self.workdir)

    def close(self):
        promise =  self.rpc.close_project(project_id=self.data.id,branch=self.branch)
        promise.bind('success',self,'closed')
        return promise

    def commit(self,message='Commit message'):
        return self.rpc.commit(project_id=self.data.id,message=message,branch=self.branch)

    def write(self,path,contents):
        return self.rpc.write(path,contents,project_id=self.data.id,branch=self.branch)

    def read(self,path,revision=None):
        return self.rpc.read(path,revision=revision,project_id=self.data.id,branch=self.branch)

    def query(self,pattern='WORKDIR:^(?!.git).*$'):
        return self.rpc.query(pattern,project_id=self.data.id,branch=self.branch)

@async_class
class ProjectService(Service):

    @interruptible_init
    def __init__(self):
        super(ProjectService,self).__init__()
        self.project_list = []
        self.open_projects = []
        self._rpc_project = yield RPCClientFactory.get_client('project')
        self._rpc_projectfs = yield RPCClientFactory.get_client('projectfs')
        self.project_list = yield self._rpc_projectfs.query()

    @interruptible
    def open_project(self,project_id,branch='master'):
        try:
            for p in self.open_projects:
                if p.data.id == project_id and p.branch == branch:
                    logger.info("Project already open:", p.data.title, "(id:",project_id,",branch:",branch,")")
                    yield Return(p)
            project_data = yield self._rpc_project.open(project_id,branch=branch)
            project = Project(self._rpc_project,project_data)
            self.open_projects.append(project)
            project.bind('closed',self._close_project)
            yield project._load_workdir()
            yield Return(project)
        except Exception as ex:
            logger.log("Exception when opening project:",ex)
            logger.exception(ex)

    def _close_project(self,event):
        proj = event.target
        self.open_projects.remove(proj)







