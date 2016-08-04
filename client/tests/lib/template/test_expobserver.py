from client.python_packages.lib.template.expobserver import ExpObserver
from client.python_packages.lib.template.context import Context
from client.tests.utils import TestObserver

def test_obj_observer():
    ctx = Context()
    ctx.lst = [-4,-3,-2,-1,0,1,2,3,4]
    ctx.a = 1
    ctx.b = -2
    ctx.c = 0.5

    obs = ExpObserver("a*x**2 + b*x + c*x",ctx)
    assert obs.have_value() == False
    t = TestObserver(obs)

    ctx.d=10
    assert len(t.events) == 0

    ctx.x = 0
    data =  t.events.pop().data
    assert data['new'] == 0
    assert 'old' not in data
    assert obs.have_value() == True
    assert obs.value() == 0

