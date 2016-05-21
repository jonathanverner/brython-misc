import lib.angular.core as ngcore
from services import ServiceFactory, StatusService

from lib.logger import Logger
logger = Logger('status_bar.py')


@ngcore.component
class StatusBarComponent(ngcore.Component):

    class ComponentData:
        selector = 'ide-status-bar'
        templateUrl = "app/templates/ide/status-bar.component.html"
        directives = []


    def __init__(self):
        super(StatusBarComponent,self).__init__()
        self.status_service = ServiceFactory.get_service(StatusService)
        logger.log("Service",self.status_service)

