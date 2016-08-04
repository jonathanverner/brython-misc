def generate_forward_handler(obj,forward_event):
    def handler(ev):
        obj.emit(forward_event,ev,_forwarded=True)
    return handler

class Event:
    def __init__(self, name, target, data=None):
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


def add_event_mixin(obj):
    """Apply mixins to a class instance after creation"""
    base_cls = obj.__class__
    base_cls_name = obj.__class__.__name__
    obj.__class__ = type(base_cls_name, (EventMixin,base_cls),{})
    obj._event_handlers = {}


class EventMixin:
    """
        A Mixin class which adds methods to an object to make it possible
        for it to emit events and for others to bind to its emitted events
    """

    def __init__(self):
        self._event_handlers = {}
        self._forwarding_from_objects = []

    def bind(self, event, handler, forward_event=None):
        """
           Registers an event handler for event. If @forward_event is provided
           and handler is an object, registers a handler which emits the
           event @forward_event on object @handler whenever the current object
           emits the event @event.
        """
        if forward_event is not None and isinstance(handler,EventMixin):
            h = generate_forward_handler(handler,forward_event)
            handler._forwarding_from_objects.append((self,h,event))
            handler = h

        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def stop_forwarding(self,event = None):
        """
           Stops forwarding all events
        """
        retain = []
        for (obj,h,e) in self._forwarding_from_objects:
            if event is None or e == event:
                obj.unbind(e,h)
            else:
                retain.append((obj,h,e))
        self._forwarding_from_objects = retain


    def unbind(self,event=None,handler=None):
        """
           Unregisters event handlers.

           If @event is None, unregisters ALL handlers for all events.

           If @event is provided and not an EventMixin but @handler is None,
           unregisters all handlers for event @event.

           Otherwise unregisters only the specified @handler from the event @event.
        """
        if event is None:
            self._event_handlers = {}
            for (obj,h,event) in self._forwarding_from_objects:
                obj.unbind(event,h)
            self._forwarding_from_objects = []
        else:
            handlers = self._event_handlers.get(event,[])
            if handler is None:
                handlers.clear()
            else:
                handlers.remove(handler)

    def emit(self, event, event_data=None,_forwarded=False):
        """
            Emits an envent on the object, calling all event handlers. Each
            event handler will be passed an object of type Event whose
            @data attribute will contain @event_data and @targets and @names@
            attribute will be a list of objects on which the event was called
            starting from the first one and going up along the forwarding chain
            (if forward handlers were registered).

            NOTE: _forwarded should NOT be set by the users. If is used
            internally by forward handlers to indicate that this is a
            forwarded event.
        """
        if _forwarded and isinstance(event_data, Event):
            event_data.retarget(self)
            event_data.rename(event)
        else:
            event_data = Event(event, self, event_data)
        handlers = self._event_handlers.get(event,[])
        for h in handlers:
            h(event_data)