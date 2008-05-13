##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2008  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the BSD style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from . import sqlCreateStorage as _sql

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SQLStorage(object):
    nextOid = None
    _sql_init = [
        _sql.createLookupTables,
        _sql.createStorageTables,
        _sql.createExternalTables,
        _sql.createLookupViews,
        _sql.createOidReferenceViews,
        ]

    def __init__(self, db, nextOid=None):
        self.db = db
        self.cursor = db.cursor()
        if nextOid is not None:
            self.nextOid = nextOid

        self.initialize()

    def initialize(self):
        for sql in self._sql_init:
            self.cursor.executescript(sql)

    def commit(self):
        return self.db.commit()

    def __getstate__(self):
        raise RuntimeError("Tried to store storage mechanism: %r" % (self,))

    def allOids(self):
        r = self.cursor.execute(
            'select oid from oid_lookup')
        return [e[0] for e in r.fetchall()]

    def allOidInfo(self):
        r = self.cursor.execute(
            'select * from oid_lookup')
        return r.fetchall()

    def getOidInfo(self, oid):
        r = self.cursor.execute(
            'select stg_kind, otype '
            '  from oid_lookup where oid=?', (oid,))
        return r.fetchone()

    def setOid(self, obj, oid, stg_kind, otype):
        if oid is None:
            oid = self.nextOid
            self.nextOid = oid+1

        if not isinstance(oid, int): 
            raise ValueError("Object oid must be specified")
        if not isinstance(stg_kind, str): 
            raise ValueError("Object storage stg_kind must be specified")

        self.cursor.execute(
            'replace into oid_lookup (oid, stg_kind, otype) '
            '  values(?, ?, ?)', (oid, stg_kind, otype))
        return oid

    def allURLPaths(self, incOid=True):
        if incOid:
            r = self.cursor.execute(
                "select urlpath, oid_ref from exports")
            return r.fetchall()
        else:
            r = self.cursor.execute(
                "select urlpath from exports")
            return [e[0] for e in r.fetchall()]

    def getAtURLPath(self, urlpath):
        r = self.cursor.execute(
            "select oid, stg_kind, otype from exports_lookup"
            "  where urlpath=?", (urlpath,))
        return r.fetchone()

    def setURLPathForOid(self, urlpath, oid):
        self.cursor.execute(
            "replace into exports (urlpath, oid_ref)"
            "  values(?,?)", (urlpath, oid))

    def findLiteral(self, value, value_hash, value_type):
        r = self.cursor.execute(
            'select oid from literals '
            '  where value=? and value_hash=? and value_type=?',
            (value, value_type, value_hash))
        return r.fetchone()

    def getLiteralAndType(self, oid):
        r = self.cursor.execute(
            'select value, value_type '
            '  from literals where oid=?', (oid,))
        return r.fetchone()

    def getLiteral(self, oid):
        r = self.cursor.execute(
            'select value from literals ' 
            '  where oid=?', (oid,))
        r = r.fetchone()
        if r is not None:
            return r[0]
    def setLiteral(self, value, value_hash, value_type, stg_kind):
        oid = self.findLiteral(value, value_hash, value_type)
        if oid is not None:
            return oid

        oid = self.setOid(value, None, stg_kind, value_type)
        self.cursor.execute(
            'insert into literals (oid, value, value_type, value_hash)'
            '  values(?, ?, ?, ?)', (oid, value, value_type, value_hash))
        return oid

    def getWeakref(self, oid):
        r = self.cursor.execute(
            'select v_oid, v_stg_kind, v_otype from weakrefs_lookup '
            '  where oid_host=?', (oid,))
        return r.fetchone()
    def setWeakref(self, oid, oid_ref):
        self.cursor.execute(
            'insert into weakrefs (oid_host, oid_ref)'
            '  values(?, ?)', (oid, oid_ref))
        return oid

    def getOrdered(self, oid):
        r = self.cursor.execute(
            'select '
            '    v_oid, v_stg_kind, v_otype '
            '  from lists_lookup where oid_host=?', (oid,))
        return r.fetchall()
    def setOrdered(self, oid, valueOids):
        self.cursor.execute(
            'delete from lists '
            '  where oid_host=?', (oid,))

        self.cursor.executemany(
            'insert into lists values(NULL, ?, ?)',
            ((oid, oid_v) for oid_v in valueOids))
        return oid

    def getMapping(self, oid):
        r = self.cursor.execute(
            'select '
            '    k_oid, k_stg_kind, k_otype, '
            '    v_oid, v_stg_kind, v_otype '
            '  from mappings_lookup where oid_host=?', (oid,))
        return [(e[:3], e[3:]) for e in r.fetchall()]
    def setMapping(self, oid, itemOids):
        self.cursor.execute(
            'delete from mappings '
            '  where oid_host=?', (oid,))

        self.cursor.executemany(
            'insert into mappings values(NULL, ?, ?, ?)',
            ((oid, oid_k, oid_v) for oid_k, oid_v in itemOids))
        return oid
