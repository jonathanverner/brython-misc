#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado.gen import coroutine, Return
from ..lib.tornado import RPCService, RPCException, export
from ..lib import update_params

class UserService(RPCService):
    SERVICE_NAME = 'user'
    user_editable_profile_attrs = ['name','surname']

    class User:
        def __init__(self,data):
            for (k,v) in data.items():
                setattr(self,k,v)

        @classmethod
        def anonymous(cls):
            return cls({
                'name':'Anonymous',
                'surname':'Anonumous',
                'email':'invalid@invalid.com',
                'id':None
            })


    def __init__(self, server_api):
        super(UserService,self).__init__(server_api)

    @classmethod
    def on_open(cls,server_api):
        print("Registering Default Anonymous User")
        server_api.session.user = UserService.User.anonymous()

    @export
    def get_profile(self):
        return self._api.session.user

    @export
    def update_profile(self,profile):
        update_params(self.session.user,profile,self.user_editable_profile_attrs)
        yield self._api.store.save(self.session.user)

    @export
    def query(self, query):
        return self._api.store.query('users',query)

    @export
    def login(self,email,password=None):
        users = yield self._api.store.query('users',{'email':email})
        if len(users) > 0:
            print(users)
            self._api.session.user=UserService.User(users[0])
            return self._api.session.user
        raise RPCException('Invalid user or password: '+email)


services = [UserService]


