import client.python_packages.lib.template.observer as o
from client.tests.utils import TestObserver

class MockObj(object):
    def __init__(self,v):
        self.v = v

def test_obj_observer():
    m = MockObj(10)
    ob1 = o.observe(m)
    ob2 = o.observe(m)

    t1 = TestObserver(ob1)
    t2 = TestObserver(ob2)

    m.v = 20

    ev1 = t1.events.pop()
    ev2 = t2.events.pop()
    assert ev1 == ev2
    assert ev1.data == {
        'observed_obj':m,
        'type':'__setattr__',
        'key':'v',
        'value':20,
    }

def test_dict_observer():

    d = o.DictProxy({'a':10})
    obs = o.observe(d)
    t = TestObserver(obs)

    d['a'] = 30
    assert t.events.pop().data == {
        'observed_obj':d,
        'type':'__setitem__',
        'key':'a',
        'value':30,
        'old':10
    }

def test_list_observer():

    l = o.ListProxy([1,2,3,4])
    obs = o.observe(l)
    t = TestObserver(obs)

    l.pop()
    assert t.events.pop().data == {
        'observed_obj':l,
        'type':'__delitem__',
        'key':3,
        'old':4
    }
