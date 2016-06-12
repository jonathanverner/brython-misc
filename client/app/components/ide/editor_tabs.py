import lib.angular.core as ngcore


@ngcore.component
class EditorTabsComponent(ngcore.Component):

    class ComponentData:
        selector = 'ide-editor-tabs'
        templateUrl = "app/templates/ide/editor-tabs.component.html"
        directives = []


    def __init__(self):
        super(EditorTabsComponent,self).__init__()