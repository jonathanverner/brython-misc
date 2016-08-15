from lib.events import EventMixin
from browser import html
from .expobserver import ExpObserver
import re

class InterpolatedStr(EventMixin):
    def __init__(self,string,ctx):
        super().__init__()
        self.pieces = []
        self._ctx = ctx
        self._val = None
        self.src = string
        if '{{' in self.src:
            for p in self.src.split('{{')[1:]:
                if '}}' not in p:
                    self.pieces.append('{{'+p)
                else:
                    exp = '}}'.join(p.split('}}')[:-1])
                    observer = ExpObserver(exp,ctx)
                    observer.bind('change',self._change_handler)
                    self.pieces.append(observer)
        else:
            self.pieces.append(self.src)
        self.update()

    @property
    def context(self):
        return self._ctx

    @context.setter
    def context(self,ct):
        self._ctx.reset(ct)

    def value(self):
        return self._val

    def update(self):
        self._val = ""
        for p in self.pieces:
            if isinstance(p,ExpObserver):
                if p.have_value():
                    self._val += str(p.value())
            else:
                self._val += p

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
    def value(self):
        return self._attr.value

    @value.setter
    def value(self,val):
        self._interpolated.unbind()
        self._interpolated = None
        self._attr.value = val

    @property
    def context(self):
        return self._ctx

    @context.setter
    def context(self,ct):
        self._ctx = ct
        if self._interpolated is not None:
            self._interpolated.context = ct


    @property
    def interpolated(self):
        return self._interpolated.src

    @interpolated.setter
    def interpolated(self,value):
        self._interpolated.unbind()
        self._interpolated = InterpolatedStr(value,self.context)
        self._interpolated.bind('change',self._change_handler)
        self._attr.value = self._interpolated.value()

    def is_interpolated(self):
        return self._interpolated is not None

    def _change_handler(self,event):
        self._attr.value = event.data['value']

class InterpolatedTextNode(object):
    def __init__(self,node,context):
        self._int = InterpolatedStr(node.text,context)
        self._int.bind('change',self._change_handler)
        self._node = node
        self._ctx = context

    @property
    def context(self):
        return self._ctx

    @context.setter
    def context(self,ct):
        self._int.context = ct
        self._ctx = ct

    def _change_handler(self,event):
        self._node.text = event.data['value']

class AttrDict(object):
    def __init__(self,element,context=None,interpolate = True):
        self._attrs = {}
        self._ctx = context
        self._elem = element
        for a in self._elem.attributes:
            val = a.value
            self._attrs[a.name] = InterpolatedAttr(a,self._ctx)
            if interpolate is False or (interpolate is not True and a.name not in interpolate):
                self._attrs[a.name].value = val
        self._interpolate = interpolate

    @property
    def context(self):
        return self._ctx

    @context.setter
    def context(self,ct):
        self._ctx = ct
        for (a,data) in self._attrs.items():
            data.context = ct

    @property
    def interpolate(self):
        ret = []
        for (attr_name,data) in self._attrs.items():
            if data.is_interpolated():
                ret.append(attr_name)
        return ret

    @interpolate.setter
    def interpolate(self,dct=True):
        for (attr_name,data) in self._attrs.items():
            if (dct is True or attr_name in dct) and not data.is_interpolated():
                data.interpolated = data.value

    def __iter__(self):
        return iter(self._attrs)

    def keys(self):
        return self._attrs.keys()

    def items(self):
        return self._attrs.items()

    def __getitem__(self, key):
        return self._attrs[key].value

    def __setitem__(self, key, value):
        a = self._attrs[key]
        if a.is_interpolated():
            a.interpolated = value
        else:
            a.value = value


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