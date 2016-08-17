from unittest.mock import patch
import client.tests.brython.browser
from client.python_packages.lib.template.context import Context
from client.python_packages.lib.template.tag import InterpolatedAttr, AttrDict


from client.python_packages.lib.events import EventMixin
from client.python_packages.lib.template.expobserver import ExpObserver
from client.python_packages.lib.template.expression import ET_INTERPOLATED_STRING, parse
class InterpolatedStr(EventMixin):
    def __init__(self,string):
        super().__init__()
        self.observer = ExpObserver(string,Context(),expression_type=ET_INTERPOLATED_STRING)
        self.observer.bind('change',self._change_handler)

    def bind_ctx(self,ctx):
        self.observer.context = ctx

    @property
    def src(self):
        return self.observer._exp_src

    @property
    def context(self):
        return self.observer.context

    @context.setter
    def context(self,ct):
        self.observer.context = ct

    @property
    def value(self):
        return self.observer.value()

    def _change_handler(self,event):
        old,new  = event.data.get('old',""), event.data.get('new',"")
        self.emit('change',{'old':old,'value':new})

    def __repr__(self):
        return "InterpolatedStr("+self.src.replace("\n","\\n")+") = "+self._val


def test_incomplete():
    ctx = Context()
    s = InterpolatedStr("Ahoj {{ name }} {{ surname }}!")
    assert s.value == "Ahoj  !"

    ctx.name = "Jonathan"
    s.bind_ctx(ctx)
    assert s.value == "Ahoj Jonathan !"

    ctx.surname = "Verner"
    assert s.value == "Ahoj Jonathan Verner!"

class MockAttr:
    def __init__(self,name,val=None):
        self.name = name
        self.value = val

class MockElement:
    def __init__(self,tag_name):
        self.attributes = []
        self.elt = MockDomElt()

class MockDomElt:
    def __init__(self):
        pass

    def removeAttribute(self,attr):
        pass

def test_interpolated_attr():
    ctx = Context()
    a = MockAttr("class","{{ ' '.join(classes) }}")
    ia = InterpolatedAttr(a,ctx)
    assert a.value == ""

    ctx.classes=['ahoj','cau']
    assert a.value == "ahoj cau"

    del ctx.classes
    assert a.value == ""

def test_attr_dict():
    ctx = Context()
    ctx.name="Jonathan"
    el = MockElement('div')
    ida = MockAttr('id','test')
    naa = MockAttr('name','{{ name }}')
    exa = MockAttr('excluded','{{ name }}')
    el.attributes.extend([ida,naa,exa])

    ad = AttrDict(el,['excluded'])
    assert ida.value == 'test'
    assert naa.value == ""
    assert exa.value == "{{ name }}"
    assert ad['id'] == 'test'
    assert ad['name'] == ''
    assert ad['excluded'] == '{{ name }}'

    ad.bind_ctx(ctx)
    assert ida.value == 'test'
    assert naa.value == "Jonathan"
    assert exa.value == "{{ name }}"
    assert ad['id'] == 'test'
    assert ad['name'] == 'Jonathan'
    assert ad['excluded'] == '{{ name }}'

    ctx.name="Ansa"
    assert naa.value == "Ansa"
    assert ad['name'] == 'Ansa'
    assert ad['excluded'] == '{{ name }}'








