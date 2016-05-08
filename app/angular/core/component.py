import javascript
from browser import window, document, console
from .jsdict import JSDict

class Component:
    METADATA = ['selector','template','templateURL','pipes','providers','styles','styleUrls','renderer']
    _component = None

    def __init__(self):
        console.log("Initializing Component:", self.__class__.__name__)
        if hasattr(self,'ComponentData') and hasattr(self.ComponentData,'Inputs'):
            for k in dir(self.ComponentData.Inputs):
                if k[0] != '_':
                    console.log("Setting default for", k)
                    setattr(self,k,getattr(self.ComponentData.Inputs,k))
        pass

def _js_constructor(cls):
    def constr():
        obj = cls()
        #return javascript.pyobj2jsobj(obj)
        return window.modules.js.pyobj2js(obj)
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

    meta = JSDict(attr_dict)
    jscls = JSDict(_get_js_annots(cls))
    console.log("Meta:",meta)
    console.log("CLS:",jscls)
    window[str(cls)]=cls

    cls._component = window.ng.core.Component(meta).Class(jscls)
    window.ng.platformBrowserDynamic.bootstrap(cls._component)
    return cls