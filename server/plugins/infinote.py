#!/usr/bin/env python
# -*- coding:utf-8 -*-

from ..lib import EndpointHandler, event
import lib.infinote as infinote

class InfinoteEndpoint(EndpointHandler):
    _open_files = {}
    _projpath_to_handle = {}
    _next_handle = 0

    @event('open file')
    def open_file(self, projectid, path):
        if (projectid,path) not in InfinoteEndpoint._projpath_to_handle:
            proj = self.session.open_projects.get(projectid,None)
            if proj is None:
                return {'Error':'Project '+projectid+' not open'}
            content = proj['files'].get(path,None)
            if content is None:
                return {'Error':'File '+path+' not found in project '+projectid}
            fd = {
                "state":infinote.State(infinote.Buffer([infinote.Segment(proj['owner'],content)])),
                "editing":[self.session.user],
                "handle":InfinoteEndpoint._next_handle,
            }
            InfinoteEndpoint._open_files[InfinoteEndpoint._next_handle]=fd
            InfinoteEndpoint._next_handle += 1
        else:
            handle = InfinoteEndpoint._projpath_to_handle[(projectid,path)]
            fd = InfinoteEndpoint._open_files[handle]
            fd['editing'].append(self.session.user)
        seg = infinote.Segment(proj['owner'],content)
        print infinote.objectToDict(infinote.Segment(proj['owner'],content))
        print content
        print seg.user, seg.text
        return infinote.objectToDict(fd)

    @event('edit request')
    def edit_req(self, handle, request):
        fd = InfinoteEndpoint._open_files.get(handle,None)
        if fd is None:
            return {'Error':'Handle '+handle+' does not referr to an open file.'}
        request = infinote.objectFromDict(request)
        fd['state'].execute(request)

        print infinote.objectToDict(request), ''.join(fd['state'].buffer)

endpoints = [('/infinote',InfinoteEndpoint)]