from browser import console
from jsconverters import pyobj2js

def export2js(func):
    def constructor(self,*args,**kwargs):
        func(self,*args,**kwargs)
        console.log("Exporting to js")
        pyobj2js(self)
    return constructor