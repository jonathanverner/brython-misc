import lib.angular.core as ngcore


@ngcore.component
class MenuBarComponent(ngcore.Component):

    class ComponentData:
        selector = 'ide-menu-bar'
        templateUrl = "app/templates/ide/menu-bar.component.html"
        directives = []


    def __init__(self):
        super(MenuBarComponent,self).__init__()