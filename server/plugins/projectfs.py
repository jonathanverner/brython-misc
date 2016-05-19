#!/usr/bin/env python
# -*- coding:utf-8 -*-

from ..lib import EndpointHandler, event, update_params
from ..lib.auth import logged_in, auth

class ProjectFSEndpoint(EndpointHandler):
    @event('query')
    @logged_in
    def query(self,query):
        query['user_id'] = self.user.id
        return self.store.get('projectfss',query)

    @event("move label")
    @logged_in
    def move_label(self,orig,dest):
        pass

    @event('remove label')
    @logged_in
    def remove_label(self,label):
        pass

    @event('create_label')
    @logged_in
    def create_label(self,path):
        pass

    @event('label')
    @logged_in
    def label(self,project_id,path):
        pass





endpoints = [('/projectfs',ProjectFSEndpoint)]


