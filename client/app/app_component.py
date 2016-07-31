import lib.angular.core as ngcore
from components.ide import EditorTabsComponent, MenuBarComponent, ProgressBarComponent, ProjectTreeComponent, StatusBarComponent
from components.widgets import ConsoleComponent
from services import UserService, ProjectService, ProgressService, StatusService



@ngcore.component
class AppComponent(ngcore.Component):

    class ComponentData:
        selector = 'ide-app'
        templateUrl = "app/templates/app.component.html"
        directives = [EditorTabsComponent, MenuBarComponent, ProgressBarComponent, ProjectTreeComponent, StatusBarComponent, ConsoleComponent]

        services = {
            'user':UserService,
            'project':ProjectService,
            'progress':ProgressService,
            'status':StatusService
        }


    def __init__(self):
        super(AppComponent,self).__init__()
        self.services.user.login('jonathan@temno.eu',None)






