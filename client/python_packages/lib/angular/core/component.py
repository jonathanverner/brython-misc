import javascript
from browser import document
from .jsdict import JSDict
from .services import ServiceFactory
from jsmodules import jsimport
from jsconverters import pyobj2js
from lib.logger import Logger

jsng = jsimport('ng')
logger = Logger(__name__,level=Logger.SEVERITY_ERROR)

class _ng:
    class core:
        ViewChild = javascript.JSConstructor(jsng.core.ViewChild)

class Query:
    def to_js(self):
        return javascript.pyobj2jsobj(self._ng_obj)

class ViewChild(Query):
    def __init__(self, reference):
        if hasattr(reference,'_component'):
            self._ref = reference
        else:
            self._ref = reference
        self._ng_obj = _ng.core.ViewChild(self._ref)

_Output = javascript.JSConstructor(jsng.core.EventEmitter)

def Output():
    out = _Output()
    ret=javascript.pyobj2jsobj(out)
    ret.pyobj = out
    ret.emit = out.emit
    def pub(ch):
        ret.pyobj.emit(ch)
    def sub(f,error=None,compl=None):
        ret.pyobj.subscribe(f,error,compl)
    ret.pub = pub
    ret.sub = sub
    return ret

class directives:
    class Self:
        pass

class Component:
    METADATA = ['selector','template','templateUrl','pipes','providers','styles','styleUrls','renderer']
    _component = None

    class _obj:
        pass


    def __init__(self):
        logger.debug("Initializing Component:", self.__class__.__name__)
        if hasattr(self,'ComponentData'):
            if hasattr(self.ComponentData,'Inputs'):
                for k in dir(self.ComponentData.Inputs):
                    if k[0] != '_':
                        setattr(self,k,getattr(self.ComponentData.Inputs,k))
            if hasattr(self.ComponentData,'Outputs'):
                for k in dir(self.ComponentData.Outputs):
                    if k[0] != '_':
                        setattr(self,k,getattr(self.ComponentData.Outputs,k))
            if hasattr(self.ComponentData,'services'):
                self.services = Component._obj()
                for (name,cls) in self.ComponentData.services.items():
                    setattr(self.services,name,ServiceFactory.get_service(cls))

def _js_constructor(cls):
    def constr():
        logger.debug("Calling constructor for ", cls.__name__)
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
    js_annots = _get_js_annots(cls)
    jscls = JSDict(js_annots)
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
                elif type(d) == type(""):
                    attr_dict['directives'].append(jsimport(d))
                elif issubclass(d,directives.Self):
                    attr_dict['directives'].append(js_annots['constructor'])
                else:
                    attr_dict['directives'].append(d)

        if hasattr(data,'ViewElements'):
            attr_dict['queries'] = {}
            for k in dir(data.ViewElements):
                if not k[0] == '_':
                    val = getattr(data.ViewElements,k)
                    attr_dict['queries'][k] = val.to_js()
            attr_dict['queries'] = JSDict(attr_dict['queries'])

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
    logger.debug("Meta:",meta)
    logger.debug("CLS:",jscls)

    cls._component = jsng.core.Component(meta).Class(jscls)
    return cls

def bootstrap(component,arg=None):
    if arg is None:
        jsng.platformBrowserDynamic.bootstrap(component._component)
    else:
        jsng.platformBrowserDynamic.bootstrap(component._component,arg)