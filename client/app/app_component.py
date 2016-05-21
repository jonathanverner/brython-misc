from browser import console
import javascript
import lib.angular.core as ngcore
from components.ide import EditorTabsComponent, MenuBarComponent, ProgressBarComponent, ProjectTreeComponent, StatusBarComponent



@ngcore.component
class AppComponent(ngcore.Component):

    class ComponentData:
        selector = 'ide-app'
        templateUrl = "app/templates/app.component.html"
        directives = [EditorTabsComponent, MenuBarComponent, ProgressBarComponent, ProjectTreeComponent, StatusBarComponent]


    def __init__(self):
        super(AppComponent,self).__init__()






