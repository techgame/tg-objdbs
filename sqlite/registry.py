##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2007  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import sqlite3
from serialize import ObjectSerializer
from deserialize import ObjectDeserializer
from sqlStorage import SQLStorage

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SQLObjectRegistry(object):
    def __init__(self, filename):
        self.oids = {}
        self._initFileStorage(filename)

    def __getstate__(self):
        raise RuntimeError("Tried to store storage mechanism: %r" % (self,))

    def _initFileStorage(self, filename):
        self.db = sqlite3.connect(filename)
        self.db.isolation_level = None

        self.stg = SQLStorage(self.db.cursor(), 1000)
        self._save = ObjectSerializer(self.oids, self.stg)
        self._load = ObjectDeserializer(self.oids, self.stg)

    def store(self, obj, urlpath=None):
        return self._save.store(obj, urlpath)

    def load(self, oid):
        return self._load.load(oid)

    def allOids(self):
        return self.stg.allOids()

    def allURLPaths(self):
        return self.stg.allURLPaths()

    def close(self):
        self.db.close()

