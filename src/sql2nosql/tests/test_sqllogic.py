import csv
import datetime
import doctest
import time
import os
import shutil
import unittest
from pprint import pprint
from pprint import pformat
from collections import defaultdict
from hashlib import md5

import dateutil.parser
import pymongo
import sqlite3
import sys

#from sql2nosql import sql1

from sql2nosql import select_parser
from sql2nosql import tomongo
from sql2nosql import testing

HERE = os.path.dirname(__file__)

UNSUPPORTED = [c.strip() for c in """
CASE
EXISTS
ABS
NOT BETWEEN
""".split()]

TYPE_TO_STR = {
    type(None): 'N',
    type(0): 'I',
    type(0L): 'I',
    type(0.1): 'I',
    type('s'): 'T',
    type(u's'): 'T',
}


class SqlLogicTests(unittest.TestCase):
    columns = None
    counts = None

    def process_record(self, record):
        if record['type'].startswith('statement'):
            if 'create' in record['command'].lower():
                p = select_parser.create_stmt.parseString(record['command'])
                columns = p.columns.asList()
                table = p.asList()[2]
                self.columns[table] = columns

                cur = self.con.cursor()
                cur.execute(record['command'])
                cur.close()

            elif 'insert' in record['command'].lower():
                p = select_parser.insert_stmt.parseString(record['command'])
                table = p.asList()[2]
                columns = p.asList()[3]
                values = p.asList()[5]
                data = dict((str(c), v) for c, v in zip(columns, values))

                cur = self.con.cursor()
                cur.execute(record['command'])
                cur.close()

                self.db[str(table)].insert(data)
            else:
                # huhh?
                pass
        elif record['type'].startswith('query'):
            cur = self.con.cursor()
            cur.execute(record['command'])
            sresults = list(cur.fetchall())
            cur.close()

            typeparts = record['type'].split()
            query = typeparts[0]
            types = typeparts[1]
            sortnosort = typeparts[2]
            cmd = record['command']
            __traceback_info__ = pformat(record)
            ucmd = cmd.upper()
            for uns in UNSUPPORTED:
                if uns in ucmd:
                    self.counts['unsupported'] += 1
                    return
            if ucmd.count('SELECT') > 1:
                self.counts['unsupported'] += 1
                return

            try:
                q = tomongo.Query(record['command'])
            except tomongo.Unsupported:
                self.counts['unsupported'] += 1
                return
            record['debug'] = q.dump()
            __traceback_info__ = pformat(record)
            try:
                mresults = list(q.execute(self.db))
                mresults = list(q.sqlresults(mresults))
                if len(mresults) > 0:
                    first = mresults[0]
                    coltypes = ''.join([TYPE_TO_STR[type(fv)] for fv in first])
                    if coltypes != types:
                        print 'Column types mismatch expected: %s vs %s' % (
                            types, coltypes)
                        self.counts['failed'] += 1
                        raise ValueError()
            except tomongo.Unsupported:
                self.counts['unsupported'] += 1
                return
            except:
                print
                print q.dump()
                self.counts['failed'] += 1
                raise

            if sortnosort != 'nosort':
                print 'Dunno how to sort this'
                self.counts['failed'] += 1

            if 'hashing to' in record['results']:
                parts = record['results'].split()
                vcount = int(parts[0])
                rcount = vcount / len(types)
                if rcount != len(mresults):
                    print q.dump()
                    print 'Record count mismatch expected: %s vs %s' % (
                            rcount, len(mresults))
                    self.counts['failed'] += 1

                    raise ValueError()

                # looks like sqllogictest uses the raw bytes of the result
                # to MD5 check... that's going to be impossible to repro
                #hsh = md5()
                #for mr in mresults:
                #    hsh.update(str(mr))
                #    hsh.update('\n')
                #hsh = hsh.hexdigest()

                # let's compare the sqlite and mongo resultset
                haveerr = False
                for rowidx, (mrow, srow) in enumerate(zip(mresults, sresults)):
                    for itemidx, (mi, si) in enumerate(zip(mrow, srow)):
                        if mi != si:
                            print 'Result value mismatch at row %s, item %s, %r vs %r' % (rowidx+1, itemidx+1, mi, si)
                            haveerr = True
                if haveerr:
                    self.counts['failed'] += 1
                    raise ValueError()
            else:
                from dbgp.client import brk; brk('127.0.0.1')

        self.counts['done'] += 1

    def process_test(self, fname):
        with open(fname) as f:
            record = {'command': '', 'results': ''}
            results = False
            lineno = 0
            for line in f:
                lineno += 1
                line = line.strip()
                if not line:
                    # end of record
                    self.process_record(record)
                    record = {'command': '', 'results': '', 'line': lineno+1}
                    results = False
                elif line.startswith('#'):
                    # comment
                    pass
                elif not 'type' in record:
                    if line.startswith('statement') or line.startswith('query'):
                        #statement ok
                        #statement error
                        #query <i>&lt;type-string&gt; &lt;sort-mode&gt; &lt;label&gt;</i>
                        record['type'] = line
                    else:
                        record['condition'] = line
                else:
                    if results:
                        record['results'] += line + '\n'
                    else:
                        if line == '----':
                            # Lines following the "----" are expected results of the query
                            results = True
                        else:
                            record['command'] += line + '\n'

    def test_one(self):
        self.process_test(os.path.join(HERE, 'select1.test'))

        print
        for k, v in self.counts.items():
            print ' '*9, k, v
        print '-------'

    def cleanDB(self):
        cur = self.con.cursor()

        cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        results = list(cur.fetchall())
        for t in results:
            cur.execute("DROP TABLE IF EXISTS %s" % t)

        cur.close()

        if 'sql2nosql-test-database' in self.client.database_names():
            self.client.drop_database('sql2nosql-test-database')

    def setUp(self):
        self.columns = {}
        self.counts = defaultdict(int)
        self.con = sqlite3.connect(':memory:')
        self.client = pymongo.MongoClient("localhost", 27017)

        self.cleanDB()

        self.db = self.client['sql2nosql-test-database']

    def tearDown(self):
        self.con.close()

#
#
#def setUp(test):
#    make_test_db()
#
#
#def tearDown(test):
#    pass
#
#
#def test_suite():
#    return doctest.DocTestSuite(
#        setUp=setUp, tearDown=tearDown,
#        optionflags=DOCTEST_OPTION_FLAGS)
