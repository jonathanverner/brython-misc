#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornadio2 import SocketConnection

class EndpointHandler(SocketConnection):
    BEFORE=0
    AFTER=1
    _on_event_callbacks = {}
    _instances={}
    store = None
    default_settings = {}
    _settings = {}
    _setting_scope=''

    @classmethod
    def register_event(cls, event_name, event_handler):
        cls._events[event_name] = event_handler

    @classmethod
    def register_callback(cls, event_name, event_handler, when=0, priority=0):
        if event_name not in cls._on_event_callbacks:
            cls._on_event_callbacks[event_name] = {EndpointHandler.BEFORE:[],EndpointHandler.AFTER:[]}
        event_handler.__priority = priority
        callback_queue = cls._on_event_callbacks[event_name][when]
        for i in range(len(callback_queue)):
            if callback_queue[i].__priority < event_handler.__priority:
                callback_queue.insert(i,event_handler)
                return
        callback_queue.append(event_handler)

    def get_setting(self,key,default=None):
        return self._settings.get(self._setting_scope+'.'+key,self.default_settings.get(key,None))

    def set_setting(self,key,value):
        self._settings[self._setting_scope+'.'+key] = value


    @classmethod
    def broadcast(cls, event, value, group='ALL'):
        if group == 'ALL':
            for group in cls._instances.values():
                for inst in group:
                    inst.emit(event,value)
        else:
            for inst in cls._instances[group]:
                inst.emit(event,value)

    @classmethod
    def register_broadcast_instance(cls, instance, group):
        if group not in cls._instances:
            cls._instances[group] = []
        cls._instances[group].append(instance)

    def error(self, message=''):
        return {'Status':'Error', 'Message':message}

    def success(self, message=''):
        return {'Status':'Ok', 'Message':message}

    def on_event(self, name, args=[], kwargs=dict()):
        callbacks = self._on_event_callbacks.get(name,None)
        if callbacks is not None:
            before_queue = callbacks[EndpointHandler.BEFORE]
            after_queue = callbacks[EndpointHandler.AFTER]
        else:
            before_queue = []
            after_queue = []

        for callback in before_queue:
            try:
                if args:
                    ret = callback(*args)
                    if ret is not None:
                        args = ret
                else:
                    ret = callback(**kwargs)
                    if ret is not None:
                        kwargs = ret
            except:
                pass

        ret = super(EndpointHandler,self).on_event(name,args=args,kwargs=kwargs)

        for callback in after_queue:
            try:
                if args:
                    rt = callback(*args,return_val=ret)
                    if rt is not None:
                        rt = ret
                else:
                    kwargs['return_val'] = ret
                    rt = callback(**kwargs)
                    if rt is not None:
                        ret = rt
            except:
                pass
        return ret