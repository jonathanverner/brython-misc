import angular.core 
from browser import console

@angular.core.component
class ClickComponent(angular.core.Component):

    class ComponentData:
        selector = 'click-me'
        template = '<button (click)="click_handler()">{{ title }}</button>{{message}}'

        class Inputs:
            title = 'Click Me!'

    def __init__(self):
        super(ClickComponent,self).__init__()
        console.log("Initializing click")
        self.message = 'Not clicked'


    def click_handler(self,*args,**kwargs):
        for (k,v) in kwargs.items():
            console.log(k,":",v)
        for a in args:
            console.log(a)
        self.message = 'Clicked'

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







