#!/usr/bin/env python
# -*- coding:utf-8 -*-

from ..lib.tornado import RPCService, export

class ChatService(RPCService):
    SERVICE_NAME = 'chat'
    ROOMS = {}
    NEXT_NICK_ID = 0

    def __init__(self, server):
        print("Initializing Chat service (calling super)")
        super(ChatService,self).__init__(server)
        print("Initializing Chat service")
        self.nick = "anonymous "+str(ChatService.NEXT_NICK_ID)
        ChatService.NEXT_NICK_ID +=1

    @export
    def create_room(self,room_name):
        ChatService.ROOMS[room_name] = set()

    @export
    def join_room(self,room_name):
        if room_name in ChatService.ROOMS:
           ChatService.ROOMS[room_name].add(self)

    @export
    def set_nick(self,nick):
        self.nick = nick

    @export
    def send_message(self,message,room_name):
        for client in ChatService.ROOMS[room_name]:
            if client == self:
                continue
            client._recv_message(message,self.nick,room_name)

    @export
    def list_rooms(self):
        return list(ChatService.ROOMS.keys())

    def _recv_message(self,message, nick, room_name):
        self.server.emit('incoming message',{
            'message':message,
            'nick':nick,
            'room_name':room_name
        })

    def _joined(self,nick, room_name):
        self.server.emit('new user joined',{
            'nick':nick,
            'room_name':room_name
        })

services = [ChatService]