#!/usr/bin/env python
import os
import sys

from tornado import web, ioloop
from tornado.options import define, options, parse_command_line
from server.app import RPCEndpoint

define("port",default=8080,help="run on given port",type=int)

app = web.Application( RPCEndpoint.__urls__+[
    (r"/",RPCEndpoint),
    (r'/(.*)', web.StaticFileHandler, {'path': './client'}),
])

if __name__ == "__main__":
    parse_command_line()
    app.listen(options.port)
    ioloop.IOLoop.instance().start()