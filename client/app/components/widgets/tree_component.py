import lib.angular.core as ngcore

from lib.logger import Logger
logger = Logger(__name__)


@ngcore.component
class TreeComponent(ngcore.Component):

    class ComponentData:
        selector = 'widget-tree'
        templateUrl = "app/templates/widgets/tree.component.html"
        directives = [ngcore.directives.Self]

        class Inputs:
            depth = 0
            model = None
            children = 'children'
            icon = 'icon'
            title = 'title'
            indent = 2

        class Outputs:
            click = ngcore.Output()


    def __init__(self):
        super(TreeComponent,self).__init__()
        self._selected = []
        self._opened = []

    def click_item(self,child,event):
        ev = ngcore.JSDict({
            'event':event,
            'child':child,
        })
        self.click.pub(ev)

    def open_tree(self,child):
        if child in self._opened:
            self._opened.remove(child)
        else:
            self._opened.append(child)

    def opened(self,child):
        return child in self._opened

    def indicator_class(self,ch):
        if self.is_leaf(ch):
            return "leaf"
        elif ch in self._opened:
            return "open"
        else:
            return "closed"


    def is_leaf(self,ch):
        return getattr(ch,self.children,None) is None

    def has_children(self,ch):
        return not self.is_leaf(ch)


