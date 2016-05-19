import angular.core
from browser import console
from RPCClient import RPCClientFactory
from async import interruptible

@angular.core.component
class RPCMethodComponent(angular.core.Component):

    class ComponentData:
        selector = 'rpc-method'
        templateUrl = "app/templates/RPCMethod.component.html"

        class Inputs:
            method = ('name','args',5)
            service = None

    def __init__(self):
        super(RPCMethodComponent,self).__init__()
        self.args = []
        self.result = None


    def ngOnChanges(self,changes):
        if len(self.method) == 2:
            self._name, self._args = self.method
            self._args = self._args[1:]
            for arg in self._args:
                self.args.append(arg[2])
            self.meth = getattr(self.service,self._name)

    @interruptible
    def call_method(self,*args,**kwargs):
        console.log("Calling method ", self._name, "with args", self.args)
        self.result = yield self.meth(*self.args)


@angular.core.component
class RPCServiceComponent(angular.core.Component):

    class ComponentData:
        selector = 'rpc-service'
        templateUrl = "app/templates/RPCService.component.html"
        directives = [RPCMethodComponent]

        class Inputs:
            service = '__system__'
            url='ws://localhost:8080/'

    def __init__(self):
        super(RPCServiceComponent,self).__init__()
        self.rpc = None
        self.methods = []

    @interruptible
    def ngOnInit(self):
        console.log("Initializing Service Component for", self.service, "at", self.url)
        self.rpc = yield RPCClientFactory.get_client(self.url,self.service)
        self.methods = self.rpc.methods
        console.log("METHODS:",self.methods)
