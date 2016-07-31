import lib.angular.core as ngcore
from lib.console import Console
from lib.logger import Logger
logger = Logger(__name__)

@ngcore.component
class ConsoleComponent(ngcore.Component):

    class ComponentData:
        selector = 'widget-console'
        templateUrl = "app/templates/widgets/console.component.html"
        directives = []

        class Inputs:
            namespace = ngcore.JSDict({})
        class ViewElements:
            textarea = ngcore.ViewChild('textarea')


    def __init__(self):
        super(ConsoleComponent,self).__init__()

    def ngAfterViewInit(self):
        logger.log(self.textarea)
        self._console = Console(self.textarea)
        logger.log(self.namespace)
        self._console.editor_ns.update(self.namespace.__dict__)
        self._console.editor_ns['ns']=self.namespace
        logger.log(self._console.editor_ns)