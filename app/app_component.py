import angular.core 
from browser import console
from components import ClickComponent, CodeMirrorComponent, Doc

@angular.core.component
class AppComponent(angular.core.Component):

    class ComponentData:
        selector = 'my-app'
        template = """
<h1>My First Angular 2 App: {{ title }} </h1>
<click-me [title]="'Ahoj'"></click-me><br/>
Title: <input [(ngModel)] = "title" (keyup)="on_key($event)"/><br/>
Check: <input type='checkbox' [(ngModel)] = "checked"/><br/>
Log: {{values }}
                   """
        directives = [ClickComponent]


    def __init__(self):
        super(AppComponent,self).__init__()
        console.log("Initializing App")
        self.title='My great Title'
        self.values = ""
        self.checked=True

    def on_key(self,event):
        self.values = event.target.value
        pass







