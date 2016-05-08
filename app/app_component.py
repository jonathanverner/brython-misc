import angular.core 
from browser import console
from components import ClickComponent, CodeMirrorComponent, Doc

@angular.core.component
class AppComponent(angular.core.Component):

    class ComponentData:
        selector = 'my-app'
        template = """
<h1 #header>My First Angular 2 App: {{ title }} </h1>
<click-me [title]="'Ahoj'"></click-me><br/>
Title: <input [(ngModel)] = "title" (keyup)="on_key($event)"/><br/>
Check: <input type='checkbox' [(ngModel)] = "checked"/><br/>
Log: {{values }}<br/>
Text: {{ doc.value }} <br/>
<button (click)="clear_doc()">Clear</button><br/>
<codemirror [options]='cm_options' [doc]="doc" (change)="doc_change($event)">
</codemirror>
                   """
        directives = [ClickComponent,CodeMirrorComponent]

        class ViewElements:
            header = angular.core.ViewChild('header')


    def __init__(self):
        super(AppComponent,self).__init__()
        console.log("Initializing App")
        console.log(self)
        self.title='My great Title'
        self.values = ""
        self.checked=True
        self.doc = Doc("Ahoj, jak se mas")
        self.cm_options = angular.core.JSDict({
            'mode':angular.core.JSDict({
                'name':'python',
                'version':3
            }),
            'indentUnit':2,
            'lineNumbers':True
        })

    def clear_doc(self):
        self.doc.value = ''

    def doc_change(self,event):
        console.log(event)
        console.log("DOC:",self.doc.value)


    def on_key(self,event):
        self.values = event.target.value
        pass







