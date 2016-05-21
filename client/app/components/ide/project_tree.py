import lib.angular.core as ngcore


@ngcore.component
class ProjectTreeComponent(ngcore.Component):

    class ComponentData:
        selector = 'ide-project-tree'
        templateUrl = "app/templates/ide/project-tree.component.html"
        directives = []


        def __init__(self):
            super(ProjectTreeComponent,self).__init__()