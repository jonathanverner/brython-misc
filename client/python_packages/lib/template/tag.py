from lib.events import EventMixin
from browser import html
from .expobserver import ExpObserver
from .expression import ET_INTERPOLATED_STRING, parse
from .context import Context

import re

class InterpolatedStr(EventMixin):
    def __init__(self,string):
        super().__init__()
        self._ctx = Context()
        self._val = None
        self.src = string
        self.observer = ExpObserver(self.src,self._ctx,expression_type=ET_INTERPOLATED_STRING)
        self.observer.bind('change',self._change_handler)

    def bind_ctx(self,ctx):
        self.context = ctx

    @property
    def context(self):
        return self.observer.context

    @context.setter
    def context(self,ct):
        self.observer.context = ct

    def value(self):
        return self._val

    def update(self):
        self._val = self.observer.value()

    def _change_handler(self,event):
        self.update()
        self.emit('change',{'value':self.value()})

class InterpolatedAttr(object):
    def __init__(self,attr,context):
        self._interpolated = InterpolatedStr(attr.value,context)
        self._attr=attr
        self._interpolated.bind('change',self._change_handler)
        self._attr.value=self._interpolated.value()
        self._ctx = context

    @property
    def context(self):
        return self._ctx

    @context.setter
    def context(self,ct):
        self._ctx = ct
        if self._interpolated is not None:
            self._interpolated.context = ct

    @property
    def src(self):
        return self._interpolated.src

    @property
    def value(self):
        return self._attr.value

    @value.setter
    def value(self,value):
        self._interpolated.unbind()
        self._interpolated = InterpolatedStr(value,self.context)
        self._interpolated.bind('change',self._change_handler)
        self._attr.value = self._interpolated.value()

    def _change_handler(self,event):
        self._attr.value = event.data['value']

class AttrDict(object):
    def __init__(self,element,exclude=[]):
        self._attrs = {}
        self._ctx = Context()
        self._elem = element
        self._exclude = exclude
        for a in self._elem.attributes:
            if not a.name in exclude:
                val = a.value
                self._attrs[a.name] = InterpolatedAttr(a,self._ctx)

    @property
    def context(self):
        return self._ctx

    @context.setter
    def context(self,ct):
        self._ctx = ct
        for (a,data) in self._attrs.items():
            data.context = ct

    def __iter__(self):
        return iter(self._attrs)

    def keys(self):
        return self._attrs.keys()

    def items(self):
        return self._attrs.items()

    def __getitem__(self, key):
        return self._attrs[key].value

    def __setitem__(self, key, value):
        if key in self._attrs:
            self._attrs[key].value = value
        else:
            if key not in self._exclude:
                setattr(self._elem,key,value)
                for attr in self._elem.attributes:
                    if attr.name == key:
                        self._attrs[key] = InterpolatedAttr(attr,self._ctx)
                        return
                raise Exception("Attribute '"+key+"' cannot be set.")
            else:
                raise Exception("Attribute '"+key+"' cannot be set.")

    def __delitem__(self,key):
        del self._attrs[key]
        self._elem.elt.removeAttribute(key)


class TemplateTag(EventMixin):
    def __init__(self, dom_element,context):
        self.attrs = AttrDict(dom_element,context)
        self.context = context
        self._elem = dom_element
        self._interp_children = []
        for ch in self._elem.children:
            if ch.elt.nodeName == '#text':
                self._interp_children.append(InterpolatedTextNode(ch,context))
            else:
                self._interp_children.append(TemplateTag(ch,context))