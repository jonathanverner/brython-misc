from browser import window, document
from .jsdict import JSDict

class Component:
    METADATA = ['selector','template','templateURL','directives','providers']
    
    def __init__(self):
        attr_dict = {}
        for a in self.METADATA:
            if hasattr(self,a):
                attr_dict[a]=self.__getattribute__(a)
        comp = JSDict(attr_dict)
        cls = JSDict({
            'constructor':self.__init__,
        })
        
        self._component = window.ng.core.Component(comp).Class(cls)
    
    def register(self):
        window.ng.platformBrowserDynamic.bootstrap(self._component)