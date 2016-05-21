import lib.angular.core as ngcore


@ngcore.component
class ProgressBarComponent(ngcore.Component):

    class ComponentData:
        selector = 'ide-progress-bar'
        templateUrl = "app/templates/ide/progress-bar.component.html"
        directives = []
        services = {
            'progress':ProgressService
        }


        def __init__(self):
            super(ProgressBarComponent,self).__init__()
