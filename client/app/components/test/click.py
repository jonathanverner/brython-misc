import lib.angular.core as ngcore
from browser import console

@ngcore.component
class ClickComponent(ngcore.Component):

    class ComponentData:
        selector = 'click-me'
        template = '<button (click)="click_handler()">{{ title }}</button>{{message}}'

        class Inputs:
            title = 'Click Me!'

    def __init__(self):
        super(ClickComponent,self).__init__()
        self.message = 'Not clicked'


    def click_handler(self,*args,**kwargs):
        for (k,v) in kwargs.items():
            console.log(k,":",v)
        for a in args:
            console.log(a)
        self.message = 'Clicked'
