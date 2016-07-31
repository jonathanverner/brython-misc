#!/usr/bin/env python
# -*- coding:utf-8 -*-

class DictStore(object):
    def __init__(self):
        pass

    def query(self, collection, query):
        raise NotImplementedError()

    def get(self, collection, id):
        raise NotImplementedError()

    def save(self, collection, dictionary):
        raise NotImplementedError()

    def create_index(self, collection, attribute):
        pass


import json
import os

from tornado.concurrent import run_on_executor, futures
from tornado import ioloop

class FileStore(DictStore):

    def __init__(self,filename=None):
        self.filename = filename
        self.io_loop = ioloop.IOLoop.current()
        self.executor = futures.ThreadPoolExecutor(8)
        if self.filename and os.path.exists(filename):
            db = json.load(open(filename,'r'))
            self.collections = db['collections']
        else:
            self.collections={}

    def __str__(self):
        return 'FileStore('+self.filename+')'

    @run_on_executor
    def get(self,collection,id):
        coll = self.collections.get(collection,None)
        if coll is not None:
            ret = coll.get(id,None)
            return ret
        else:
            return None

    @run_on_executor
    def save(self,collection,obj):
        if collection not in self.collections:
            self.collections[collection] = {}
        self.collections[collection][obj['id']]=obj

    @run_on_executor
    def query(self,collection,query):
        result_set = []
        for (id,obj) in self.collections.get(collection,{}).items():
            matches=True
            for attr in query.keys():
                if obj.get(attr,None) != query[attr]:
                    matches = False
            if matches:
                ret = dict(obj)
                ret['id'] = str(id)
                result_set.append(ret)
        return result_set

    @run_on_executor
    def persist(self):
        json.dump(open(self.filename,'w'),{'collections':self.collections})

    def __del__(self):
        #self.persist()
        pass




