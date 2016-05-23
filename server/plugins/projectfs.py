#!/usr/bin/env python
# -*- coding:utf-8 -*-

from ..lib.tornado import RPCService, export

class ProjectFSService(RPCService):
    SERVICE_NAME = 'projectfs'

    @export
    def query(self,query={}):
        query['user_id'] = self._api.session.user.id
        ret = yield self._api.store.query('projectfss',query)
        return ret

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

