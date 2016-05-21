import lib.angular.core as ngcore
from services import StatusService

from lib.logger import Logger
logger = Logger('status_bar.py')


@ngcore.component
class StatusBarComponent(ngcore.Component):

    class ComponentData:
        selector = 'ide-status-bar'
        templateUrl = "app/templates/ide/status-bar.component.html"
        directives = []
        services = {
            'status':StatusService
        }


    def __init__(self):
        super(StatusBarComponent,self).__init__()

