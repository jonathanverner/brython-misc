#!/usr/bin/env python
# -*- coding:utf-8 -*-

from ..lib import EndpointHandler, event, update_params
from ..lib.auth import logged_in, auth

class UsersEndpoint(EndpointHandler):
    user_editable_profile_attrs = ['name','surname']

    @event('get profile')
    @logged_in
    def get_profile(self):
        return self.session.user

    @event('update profile')
    @logged_in
    def update_profile(self,profile):
        update_params(self.session.user,profile,self.user_editable_profile_attrs)
        self.storage.save(self.session.user)

    @event('query')
    @auth('query users')
    def query(self, query):
        return self.storage.query('users',query)


endpoints = [('/users',UsersEndpoint)]


