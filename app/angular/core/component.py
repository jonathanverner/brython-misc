from browser import window, document
from .jsdict import JSDict

class Component:
    
    def __init__(self):
        comp = JSDict({
            'selector':self.selector,
            'template':self.template
        })
        cls = JSDict({
            'constructor':self.__init__,
        })
        
        self._component = window.ng.core.Component(comp).Class(cls)
    
    def register(self):
        window.ng.platformBrowserDynamic.bootstrap(self._component)