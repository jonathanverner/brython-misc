from browser import console
from jsconverters import pyobj2js

def export2js(func):
    def constructor(self,*args,**kwargs):
        func(self,*args,**kwargs)
        pyobj2js(self)
    return constructor

def export2jscls(cls):
    if hasattr(cls,'__init__'):
        def constructor(self,*args,**kwargs):
            cls.__init__(self,*args,**kwargs)
            pyobj2js(self)
        cls.__init__ = constructor
    return cls

