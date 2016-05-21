#!/usr/bin/env python
# -*- coding:utf-8 -*-

from tornado.gen import coroutine
from ..lib.tornado import RPCService, export
from ..lib import update_params

class UserService(RPCService):
    SERVICE_NAME = 'user'
    user_editable_profile_attrs = ['name','surname']

    def __init__(self, server):
        super(UserService,self).__init__(server)
        self.session.user={
            'name':'Anonymous',
            'surname':'Anonumous',
            'email':'invalid@invalid.com'
        }

    @export
    def get_profile(self):
        return self.session.user

    @export
    def update_profile(self,profile):
        update_params(self.session.user,profile,self.user_editable_profile_attrs)
        self.storage.save(self.session.user)

    @export
    def query(self, query):
        return self.storage.query('users',query)

    @export
    @coroutine
    def login(self,email,password=None):
        users = yield self.storage.query('users',{'email':email})
        if len(users) > 0:
            self.session.user=users[0]


services = [UserService]


