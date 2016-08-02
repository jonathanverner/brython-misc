import lib.angular.core as ngcore
from components.widgets import TreeComponent
from services import ProjectService


from lib.logger import Logger
logger = Logger(__name__)


@ngcore.component
class ProjectTreeComponent(ngcore.Component):

    class ComponentData:
        selector = 'ide-project-tree'
        templateUrl = "app/templates/ide/project-tree.component.html"
        directives = [TreeComponent]
        services = {
            'projects':ProjectService
        }


    def __init__(self):
        super(ProjectTreeComponent,self).__init__()

    def open_project(self,project,branch='master'):
        self.services.projects.open_project(project.project_id,branch=branch)