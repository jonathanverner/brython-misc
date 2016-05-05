import angular.core 

class AppComponent(angular.core.Component):
    def __init__(self):
        self.selector = 'my-app'
        self.template = '<h1>My First Angular 2 App</h1>'
        super(AppComponent,self).__init__()
