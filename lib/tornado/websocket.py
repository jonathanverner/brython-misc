import json
from tornado.websocket import WebSocketHandler
from tornado import gen

class RPCService:
    def __init__(self,client_id,server):
        self._client_id = client_id
        self._server = server
        
    
    def client_disconnected(self):
        pass
    
    def client_connected(self):
        pass
    
class RemoteObjectService(RPCService):
    def __init__(self,client_id,server):
        super(RemoteObjectService,self).__init__(client_id,server)
        self._objects = {}
        self._last_object_id = 0
        
    def add_object(self,obj):
        self._objects[self._last_object_id] = obj
        self._last_object_id += 1
        return self._last_object_id -1
    
        
    
class RPCException(Exception):
    def __init__(self,message):
        super(RPCException,self).__init__(message)

class RPCSvcApi:
    def __init__(self, server, svc):
        self.svc = svc
        self.server = server
    
    def emit(self, event, data):
        self.server.emit(self.svc, event, data)
        
class WebSocketRPCServer(WebSocketHandler):
    REGISTERED_SERVICES = {}
    ACTIVE_CLIENTS = {}
    LAST_CLIENT_ID = 0
    
    
    
    @classmethod
    def _generate_client_id(cls):
        return cls.LAST_CLIENT_ID
    
    def __init__(self):
        self._client_id = WebSocketRPCServer._generate_client_id()
        self._services = {}
        self._call_id = 0
        self._object_service = RemoteObjectService(self._client_id,RPCSvcApi(self))

    def open(self):
        WebSocketRPCServer.ACTIVE_CLIENTS[self._client_id] = self
        
    def _start_service(self,name):
        if name in self._services:
            return 
        if name in WebSocketRPCServer.REGISTERED_SERVICES:
            self._services[name] = WebSocketRPCServer.REGISTERED_SERVICES[name](self._client_id,self)
        else:
            raise RPCException('No such service: ' + str(name))
        return self._services[name]

    @gen.coroutine
    def on_message(self, message):
        msg = json.loads(message)
        svc = msg['service']
        method = msg['method']
        args = msg['args']
        call_id = msg['call_id']
        svc = self._start_service(svc)
        method = getattr(svc,method)
        if hasattr(method,'__expose_to_remote'):
            result = yield method(*args['args'],**args['kwargs'])
        else:
            raise RPCException("Method not available")
            
        try:
            result = json.dumps(result)
            raise gen.Return({
                'service':svc,
                'type':'return',
                'call_id':call_id,
                'result':{
                    'type':'json',
                    'value':result
                }
            })
        except:
            objref,cls = self._object_service.add_object(result)
            raise gen.Return({
                'call_id':call_id,
                'result':{
                    'type':'objref',
                    'value':objref,
                    'class':cls
                }
            })
                
    def emit(self, service, event, event_data):
        self.write_message( {
            'service':service,
            'type':'event',
            'event':event,
            'data':event_data
        })
        

    def on_close(self):
        del self.ACTIVE_CLIENTS[self._client_id]
        for svc in self._services.values():
            svc.client_disconnected(self._client_id)
        self._object_service.client_connected(self._client_id)