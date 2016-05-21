import javascript
from browser import console

import lib.angular.core as ngcore
from jsconverters import pyobj2js
from jsmodules import jsimport
from lib.RPCClient import RPCClient

from components.test import ClickComponent, RPCServiceComponent
from components import CodeMirrorComponent, Doc




primeng = jsimport("primeng")

@ngcore.component
class TestComponent(ngcore.Component):

    class ComponentData:
        selector = 'test-app'
        templateUrl = "app/templates/test/test.component.html"
        directives = [ClickComponent,CodeMirrorComponent,RPCServiceComponent]

        class ViewElements:
            header = ngcore.ViewChild('header')


    def __init__(self):
        super(TestComponent,self).__init__()
        console.log("Initializing App")
        console.log(self)
        self.title='My great Title'
        self.values = ""
        self.checked=True
        self.doc = Doc("Ahoj, jak se mas")
        self.cm_options = ngcore.JSDict({
            'mode':ngcore.JSDict({
                'name':'python',
                'version':3
            }),
            'indentUnit':2,
            'lineNumbers':True
        })
        console.log("Creating RPCClient")
        #self.chat_service = None
        self.chat_service = RPCClient("ws://localhost:8080/",'chat')
        console.log(self.chat_service)
        #console.log("PRIME NG",primeng)

    def clear_doc(self):
        self.doc.value = ''

    def doc_change(self,event):
        console.log(event)
        pass



    def on_key(self,event):
        self.values = event.target.value
        pass







