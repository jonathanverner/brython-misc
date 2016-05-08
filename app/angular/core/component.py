import javascript
from browser import window, document, console
from .jsdict import JSDict
from jsmodules import jsimport
from jsconverters import pyobj2js

jsng = jsimport('ng')

_Output = javascript.JSConstructor(jsng.core.EventEmitter)

def Output():
    out = _Output()
    ret=javascript.pyobj2jsobj(out)
    ret.pyobj = out
    return ret




class Component:
    METADATA = ['selector','template','templateURL','pipes','providers','styles','styleUrls','renderer']
    _component = None

    def __init__(self):
        console.log("Initializing Component:", self.__class__.__name__)
        if hasattr(self,'ComponentData'):
            if hasattr(self.ComponentData,'Inputs'):
                for k in dir(self.ComponentData.Inputs):
                    if k[0] != '_':
                        setattr(self,k,getattr(self.ComponentData.Inputs,k))
            if hasattr(self.ComponentData,'Outputs'):
                for k in dir(self.ComponentData.Outputs):
                    if k[0] != '_':
                        setattr(self,k,getattr(self.ComponentData.Outputs,k))

        pass

def _js_constructor(cls):
    def constr():
        obj = cls()
        #return javascript.pyobj2jsobj(obj)
        return pyobj2js(obj)
    return constr

def _get_js_annots(cls):
    js_annots = {}
    for base_cls in cls.__bases__:
        js_annots.update(_get_js_annots(base_cls))
        if hasattr(base_cls,'_component'):
            bc = base_cls._component
            if bc is not None:
                js_annots['extends'] = bc

    for m in dir(cls):
        if not m[0] == '_':
            meth = getattr(cls,m)
            if hasattr(meth,'__call__'):
                js_annots[m] = meth
    js_annots['constructor'] = _js_constructor(cls)
    return js_annots


def component(cls):
    jscls = JSDict(_get_js_annots(cls))
    attr_dict = {}
    if hasattr(cls,'ComponentData'):
        data = cls.ComponentData
        for a in Component.METADATA:
            if hasattr(data,a):
                attr_dict[a]=getattr(data,a)
        if hasattr(data,'directives'):
            attr_dict['directives'] = []
            for d in data.directives:
                if hasattr(d,'_component') and d._component is not None:
                    attr_dict['directives'].append(javascript.pyobj2jsobj(d._component))

        if hasattr(data,'Inputs'):
            attr_dict['inputs'] = []
            for k in dir(data.Inputs):
                if not k[0] == '_':
                    attr_dict['inputs'].append(k)

        if hasattr(data,'Outputs'):
            attr_dict['outputs'] = []
            for k in dir(data.Outputs):
                if not k[0] == '_':
                    attr_dict['outputs'].append(k)

    meta = JSDict(attr_dict)
    console.log("Meta:",meta)
    console.log("CLS:",jscls)
    window[str(cls)]=cls

    window.ng.platformBrowserDynamic.bootstrap(cls._component)
    cls._component = jsng.core.Component(meta).Class(jscls)
    return cls