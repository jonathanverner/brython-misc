#!/usr/bin/env python
# -*- coding:utf-8 -*-

from ..lib.tornado import RPCService, export

class ProjectFSService(RPCService):
    SERVICE_NAME = 'projectfs'

    @export
    def query(self,query={}):
        query['user_id'] = self.session.user.id
        return self.store.get('projectfss',query)

    @export
    def move_label(self,orig,dest):
        pass

    @export
    def remove_label(self,label):
        pass

    @export
    def create_label(self,path):
        pass

    @export
    def label(self,project_id,path):
        pass

services = [ProjectFSService]

