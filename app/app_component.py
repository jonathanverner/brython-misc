import angular.core 
from browser import console
from components import ClickComponent, CodeMirrorComponent, Doc
import javascript
from jsconverters import pyobj2js

@angular.core.component
class AppComponent(angular.core.Component):

    class ComponentData:
        selector = 'my-app'
        directives = [ClickComponent,CodeMirrorComponent]
        templateUrl = "app/templates/app.component.html"

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
        pass



    def on_key(self,event):
        self.values = event.target.value
        pass







