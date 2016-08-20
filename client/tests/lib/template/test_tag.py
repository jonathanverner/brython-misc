from unittest.mock import patch
import client.tests.brython.browser
from client.python_packages.lib.template.context import Context
from client.python_packages.lib.template.tag import AttrDict


from client.python_packages.lib.events import EventMixin
from client.python_packages.lib.template.expobserver import ExpObserver
from client.python_packages.lib.template.expression import ET_INTERPOLATED_STRING, parse

class InterpolatedStr(EventMixin):
    def __init__(self,string):
        super().__init__()
        self.observer = ExpObserver(string,expression_type=ET_INTERPOLATED_STRING)
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
        return self.observer.value

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

    def clone(self):
        return MockAttr(self.name,self.value)

class MockAttrList:
    def __init__(self):
        self.atts = []

    def __getattr__(self, name):
        for a in self.atts:
            if a.name == name:
                return a
        return super().__getattribute__(name)

    def extend(self,lst):
        self.atts.extend(lst)

    def append(self,a):
        self.atts.append(a)

    def __iter__(self):
        return iter(self.atts)


class MockElement:
    def __init__(self,tag_name):
        self.tag_name = tag_name
        self.attributes = MockAttrList()
        self.elt = MockDomElt()

    def clone(self):
        ret = MockElement(self.tag_name)
        for attr in self.attributes:
            ret.attributes.append(attr.clone())
        return ret

class MockDomElt:
    def __init__(self):
        pass

    def removeAttribute(self,attr):
        pass


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
    assert naa.value == "{{ name }}"
    assert exa.value == "{{ name }}"
    assert ad['id'] == 'test'
    assert ad['name'] == '{{ name }}'
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

    elc = el.clone()
    idac,naac,exac = elc.attributes
    ctx2 = Context()
    ctx2.name="Jonathan"
    ad_c = ad.clone(elc)
    ad_c.bind_ctx(ctx2)
    assert naa.value == "Ansa"
    assert ida.value == 'test'
    assert idac.value == 'test'
    assert naa.value == "Ansa"
    assert naac.value == "Jonathan"
    assert exa.value == "{{ name }}"
    assert exac.value == "{{ name }}"
    assert ad_c['name'] == 'Jonathan'
    assert ad['name'] == 'Ansa'








