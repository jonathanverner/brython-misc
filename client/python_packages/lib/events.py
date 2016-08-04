from lib.logger import Logger
logger = Logger(__name__)

def generate_forward_handler(obj,forward_event):
    def handler(ev):
        obj.emit(forward_event,ev,_forwarded=True)
    return handler

class Event:
    def __init__(self, name, target, data):
        self.targets = [target]
        self.names = [name]
        self.data = data
        self.handled = False

    def retarget(self,tgt):
        self.targets.append(tgt)

    def rename(self,name):
        self.names.append(name)

    @property
    def name(self):
        return self.names[-1]

    @property
    def target(self):
        return self.targets[-1]



class EventMixin:

    def __init__(self):
        self._event_handlers = {}

    def bind(self, event, handler, forward_event=None):
        if forward_event is not None and isinstance(handler,EventMixin):
            handler = generate_forward_handler(handler,forward_event)
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def unbind(self,event=None,handler=None):
        if event is None:
            self._event_handlers = {}
        else:
            handlers = self._event_handlers.get(event,[])
            if handler is None:
                handlers.clear()
            else:
                handlers.remove(handler)

    def emit(self, event, event_data):
        if _forwarded and isinstance(event_data, Event):
            event_data.retarget(self)
            event_data.rename(event)
        else:
            event_data = Event(event, self, event_data)
        handlers = self._event_handlers.get(event,[])
        for h in handlers:
            h(event_data)