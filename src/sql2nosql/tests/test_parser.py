import csv
import datetime
import doctest
import time
import os
import re
import shutil
from pprint import pprint

import dateutil.parser
import pymongo
import sqlite3
import sys

from zope.testing import renormalizing

#from sql2nosql import sql1

from sql2nosql import select_parser
from sql2nosql import tomongo
from sql2nosql import testing

HERE = os.path.dirname(__file__)

CON = sqlite3.connect(':memory:')

checker = renormalizing.RENormalizing([
    (re.compile(r"ObjectId\('[0-9a-f]{24}'\)"),
     "ObjectId('4e7ddf12e138237403000000')"),
    ])


def make_test_db():
    client = pymongo.MongoClient("localhost", 27017)
    db = client['sql2nosql-test-database']
    coll = db.persons

    pfields, persons = testing.readcsv(os.path.join(HERE, 'persons.csv'))
    afields, address = testing.readcsv(os.path.join(HERE, 'address.csv'))

    if db.persons.find().count() == 0:
        for p, a in zip(persons, address):
            p['address'] = a
            coll.save(p)

    cur = CON.cursor()

    cur.execute("DROP TABLE IF EXISTS persons")
    flds = ', '.join(["%s %s" % (f[0], f[1].upper()) for f in pfields])
    cur.execute("CREATE TABLE persons(%s)" % flds)
    flds = ', '.join(["?" for f in pfields])
    for p in persons:
        data = [p[f[0]] for f in pfields]
        cur.execute("INSERT INTO persons VALUES(%s)" % flds, data)

    cur.execute("DROP TABLE IF EXISTS address")
    flds = ', '.join(["%s %s" % (f[0], f[1].upper()) for f in afields])
    cur.execute("CREATE TABLE address(%s)" % flds)
    flds = ', '.join(["?" for f in afields])
    for a in address:
        data = [a[f[0]] for f in afields]
        cur.execute("INSERT INTO address VALUES(%s)" % flds, data)

    CON.commit()
    cur.close()


def papy(sql, sql2nosqlite=False, nodump=False, sqlresults=False):
    q = tomongo.Query(sql)
    if not nodump:
        print q.dump()

    client = pymongo.MongoClient("localhost", 27017)
    db = client['sql2nosql-test-database']

    results = list(q.execute(db))
    print "Results: (%s)" % len(results)
    if sqlresults:
        sqlres = list(q.sqlresults(results))
        pprint(sqlres)
    else:
        pprint(results)

    if sql2nosqlite:
        return

    cur = CON.cursor()
    #con.row_factory = sqlite3.Row
    cur.execute(sql)

    results = list(cur.fetchall())
    print "SQLite Results: (%s)" % len(results)
    pprint(results)


def papy_compare(sql):
    q = tomongo.Query(sql)

    client = pymongo.MongoClient("localhost", 27017)
    db = client['sql2nosql-test-database']

    results = list(q.execute(db))
    mresults = list(q.sqlresults(results))

    cur = CON.cursor()
    cur.execute(sql)

    results = list(cur.fetchall())

    if len(mresults) != len(results):
        print "Result count mismatch: %s vs %s" % (len(mresults), len(results))

    for mres, sres in zip(mresults, results):
        if mres != sres:
            print "Result data mismatch:"
            print "mongo: ", mres
            print "sqlite:", sres



def doctest_pyparser():
    """
        >>> select_parser.main()
        select * from xyzzy where z > 100
        ['SELECT', [*], 'FROM', xyzzy, 'WHERE', <z > 100>]
        - columns: [*]
        - from: xyzzy
        - table: xyzzy
        - where_expr: <z > 100>
        <BLANKLINE>
        select * from xyzzy where z > 100 order by zz
        ['SELECT', [*], 'FROM', xyzzy, 'WHERE', <z > 100>, 'ORDER', 'BY', [[zz]]]
        - columns: [*]
        - from: xyzzy
        - order_by_terms: [[zz]]
        - table: xyzzy
        - where_expr: <z > 100>
        <BLANKLINE>
        select * from xyzzy
        ['SELECT', [*], 'FROM', xyzzy]
        - columns: [*]
        - from: xyzzy
        - table: xyzzy
        <BLANKLINE>
        select z.* from xyzzy
        ['SELECT', [z.*], 'FROM', xyzzy]
        - columns: [z.*]
        - from: xyzzy
        - table: xyzzy
        <BLANKLINE>
        select a, b from test_table where 1=1 and b='yes'
        ['SELECT', [a, b], 'FROM', test_table, 'WHERE', AND [<1 = 1>, <b = yes>]]
        - columns: [a, b]
        - from: test_table
        - table: test_table
        - where_expr: AND [<1 = 1>, <b = yes>]
        <BLANKLINE>
        select a, b from test_table where 1=1 and b in (select bb from foo)
        ['SELECT', [a, b], 'FROM', test_table, 'WHERE', AND [<1 = 1>, [b, 'IN', ['SELECT', [bb], 'FROM', foo]]]]
        - columns: [a, b]
        - from: test_table
        - table: test_table
        - where_expr: AND [<1 = 1>, [b, 'IN', ['SELECT', [bb], 'FROM', foo]]]
        <BLANKLINE>
        select z.a, b from test_table where 1=1 and b in (select bb from foo)
        ['SELECT', [z.a, b], 'FROM', test_table, 'WHERE', AND [<1 = 1>, [b, 'IN', ['SELECT', [bb], 'FROM', foo]]]]
        - columns: [z.a, b]
        - from: test_table
        - table: test_table
        - where_expr: AND [<1 = 1>, [b, 'IN', ['SELECT', [bb], 'FROM', foo]]]
        <BLANKLINE>
        select z.a, b from test_table where 1=1 and b in (select bb from foo) order by b,c desc,d
        ['SELECT', [z.a, b], 'FROM', test_table, 'WHERE', AND [<1 = 1>, [b, 'IN', ['SELECT', [bb], 'FROM', foo]]], 'ORDER', 'BY', [[b], [c, 'DESC'], [d]]]
        - columns: [z.a, b]
        - from: test_table
        - order_by_terms: [[b], [c, 'DESC'], [d]]
        - table: test_table
        - where_expr: AND [<1 = 1>, [b, 'IN', ['SELECT', [bb], 'FROM', foo]]]
        <BLANKLINE>
        select z.a, b from test_table left join test2_table where 1=1 and b in (select bb from foo)
        ['SELECT', [z.a, b], 'FROM', [test_table, ['LEFT', 'JOIN'], test2_table, []], 'WHERE', AND [<1 = 1>, [b, 'IN', ['SELECT', [bb], 'FROM', foo]]]]
        - columns: [z.a, b]
        - from: [test_table, ['LEFT', 'JOIN'], test2_table, []]
          - table: test2_table
        - where_expr: AND [<1 = 1>, [b, 'IN', ['SELECT', [bb], 'FROM', foo]]]
        <BLANKLINE>
        select a, db.table.b as BBB from db.table where 1=1 and BBB='yes'
        ['SELECT', [a, db.table.b AS BBB], 'FROM', [db, '.', table], 'WHERE', AND [<1 = 1>, <BBB = yes>]]
        - columns: [a, db.table.b AS BBB]
        - from: [db, '.', table]
          - database: db
          - table: table
        - where_expr: AND [<1 = 1>, <BBB = yes>]
        <BLANKLINE>
        select a, db.table.b as BBB from test_table,db.table where 1=1 and BBB='yes'
        ['SELECT', [a, db.table.b AS BBB], 'FROM', [test_table, [db, '.', table], []], 'WHERE', AND [<1 = 1>, <BBB = yes>]]
        - columns: [a, db.table.b AS BBB]
        - from: [test_table, [db, '.', table], []]
          - table: test_table
        - where_expr: AND [<1 = 1>, <BBB = yes>]
        <BLANKLINE>
        select a, db.table.b as BBB from test_table,db.table where 1=1 and BBB='yes' limit 50
        ['SELECT', [a, db.table.b AS BBB], 'FROM', [test_table, [db, '.', table], []], 'WHERE', AND [<1 = 1>, <BBB = yes>], 'LIMIT', 50]
        - columns: [a, db.table.b AS BBB]
        - from: [test_table, [db, '.', table], []]
          - table: test_table
        - limit: 50
        - where_expr: AND [<1 = 1>, <BBB = yes>]
        <BLANKLINE>
    """

def doctest_pyparser_expr():
    """

        >>> p = select_parser.expr.parseString("Age")
        >>> print p.dump()
        [Age]

        >>> p = select_parser.expr.parseString("'Age'")
        >>> print p.dump()
        ['Age']

        >>> p = select_parser.expr.parseString("COUNT(*)")
        >>> print p.dump()
        [Count('*')]

        >>> p = select_parser.expr.parseString("AVG(Age)")
        >>> print p.dump()
        [Avg(Age)]

        >>> p = select_parser.expr.parseString("AVG(Age * Number * 1.5)")
        >>> print p.dump()
        [Avg(Age * Number * 1.5)]

        >>> p = select_parser.expr.parseString("Age * Number * 1.5")
        >>> print p.dump()
        [Age * Number * 1.5]

        >>> p = select_parser.expr.parseString("Age * (Number * 1.5)")
        >>> print p.dump()
        [Age * (Number * 1.5)]

        >>> p = select_parser.expr.parseString("Age * (Number + 1.5)")
        >>> print p.dump()
        [Age * (Number + 1.5)]

        >>> p = select_parser.expr.parseString("(Age * Number) + 1.5")
        >>> print p.dump()
        [(Age * Number) + 1.5]

        >>> p = select_parser.expr.parseString("(Age * (Number / 3.14)) + 1.5")
        >>> print p.dump()
        [(Age * (Number / 3.14)) + 1.5]

        >>> p = select_parser.expr.parseString("(Age * (Number * r / 3.14)) + 1.5")
        >>> print p.dump()
        [(Age * (Number * r / 3.14)) + 1.5]
    """

def doctest_pypa_convert_basic():
    """
        >>> papy("select * from persons")
        select * from persons
        ['SELECT', [*], 'FROM', persons]
        - columns: [*]
        - from: persons
        - table: persons
        db.persons.find(
        {},
        SON([('_id', 0)]),
        )
        Results: (25)
        [{u'Age': 35,
          u'Company': u'Litronic Industries',
          u'Email': u'essie@vaill.com',
          u'Fax': u'907-345-1215',
          u'FirstName': u'Essie',
          u'LastName': u'Vaill',
          u'Married': True,
          u'Phone': u'907-345-0962',
          u'Web': u'http://www.essievaill.com',
          u'address': {u'Address': u'14225 Hancock Dr',
                       u'City': u'Anchorage',
                       u'County': u'Anchorage',
                       u'State': u'AK',
                       u'ZIP': u'99515',
                       u'id': 1},
          u'aid': 1,
          u'id': 1},
        ...

        >>> papy("select FirstName from persons")
        select FirstName from persons
        ['SELECT', [FirstName], 'FROM', persons]
        - columns: [FirstName]
        - from: persons
        - table: persons
        db.persons.find(
        {},
        SON([('_id', 0), ('FirstName', 1)]),
        )
        Results: (25)
        [{u'FirstName': u'Essie'},
         {u'FirstName': u'Cruz'},
         {u'FirstName': u'Billie'},
         {u'FirstName': u'Zackary'},
         {u'FirstName': u'Rosemarie'},
         {u'FirstName': u'Bernard'},
         {u'FirstName': u'Sue'},
         {u'FirstName': u'Valerie'},
         {u'FirstName': u'Lashawn'},
         {u'FirstName': u'Marianne'},
         {u'FirstName': u'Justina'},
         {u'FirstName': u'Mandy'},
         {u'FirstName': u'Conrad'},
         {u'FirstName': u'Cyril'},
         {u'FirstName': u'Shelley'},
         {u'FirstName': u'Rosalind'},
         {u'FirstName': u'Davis'},
         {u'FirstName': u'Winnie'},
         {u'FirstName': u'Trudy'},
         {u'FirstName': u'Deshawn'},
         {u'FirstName': u'Claudio'},
         {u'FirstName': u'Sal'},
         {u'FirstName': u'Cristina'},
         {u'FirstName': u'Cary'},
         {u'FirstName': u'Haley'}]
        SQLite Results: (25)
        [(u'Essie',),
         (u'Cruz',),
         (u'Billie',),
         (u'Zackary',),
         (u'Rosemarie',),
         (u'Bernard',),
         (u'Sue',),
         (u'Valerie',),
         (u'Lashawn',),
         (u'Marianne',),
         (u'Justina',),
         (u'Mandy',),
         (u'Conrad',),
         (u'Cyril',),
         (u'Shelley',),
         (u'Rosalind',),
         (u'Davis',),
         (u'Winnie',),
         (u'Trudy',),
         (u'Deshawn',),
         (u'Claudio',),
         (u'Sal',),
         (u'Cristina',),
         (u'Cary',),
         (u'Haley',)]


        >>> papy("select FirstName, LastName from persons")
        select FirstName, LastName from persons
        ...
        Results: (25)
        [{u'FirstName': u'Essie', u'LastName': u'Vaill'},
        ...
        SQLite Results: (25)
        [(u'Essie', u'Vaill'),
        ...

    Too bad that mongo does not respect field order

        >>> papy("select LastName, FirstName from persons")
        select LastName, FirstName from persons
        ...
        Results: (25)
        [{u'FirstName': u'Essie', u'LastName': u'Vaill'},
        ...
        SQLite Results: (25)
        [(u'Vaill', u'Essie'),
        ...


        >>> papy("select FirstName from persons where Age=18")
        select FirstName from persons where Age=18
        ['SELECT', [FirstName], 'FROM', persons, 'WHERE', <Age = 18>]
        - columns: [FirstName]
        - from: persons
        - table: persons
        - where_expr: <Age = 18>
        db.persons.find(
        {'Age': 18},
        SON([('_id', 0), ('FirstName', 1)]),
        )
        Results: (3)
        [{u'FirstName': u'Rosalind'},
         {u'FirstName': u'Davis'},
         {u'FirstName': u'Trudy'}]
        SQLite Results: (3)
        [(u'Rosalind',), (u'Davis',), (u'Trudy',)]

        >>> papy("select FirstName from persons where Age>18 AND FirstName='Mandy'")
        select FirstName from persons where Age>18 AND FirstName='Mandy'
        ['SELECT', [FirstName], 'FROM', persons, 'WHERE', AND [<Age > 18>, <FirstName = Mandy>]]
        - columns: [FirstName]
        - from: persons
        - table: persons
        - where_expr: AND [<Age > 18>, <FirstName = Mandy>]
        db.persons.find(
        {'$and': [{'Age': {'$gt': 18}}, {'FirstName': 'Mandy'}]},
        SON([('_id', 0), ('FirstName', 1)]),
        )
        Results: (1)
        [{u'FirstName': u'Mandy'}]
        SQLite Results: (1)
        [(u'Mandy',)]

    Select a subdocument field:

        >>> papy("select FirstName, address.City from persons", sql2nosqlite=True)
        select FirstName, address.City from persons
        ['SELECT', [FirstName, address.City], 'FROM', persons]
        - columns: [FirstName, address.City]
        - from: persons
        - table: persons
        db.persons.find(
        {},
        SON([('_id', 0), ('FirstName', 1), ('address.City', 1)]),
        )
        Results: (25)
        [{u'FirstName': u'Essie', u'address': {u'City': u'Anchorage'}},
        ...

    Be forgiving about having the table name in fields:

        >>> papy("select persons.FirstName, persons.address.City from persons", sql2nosqlite=True)
        select persons.FirstName, persons.address.City from persons
        ['SELECT', [persons.FirstName, persons.address.City], 'FROM', persons]
        - columns: [persons.FirstName, persons.address.City]
        - from: persons
        - table: persons
        db.persons.find(
        {},
        SON([('_id', 0), ('FirstName', 1), ('address.City', 1)]),
        )
        Results: (25)
        ...


    """

def doctest_pypa_convert_countstar():
    """
        >>> papy("select count(*) from persons")
        select count(*) from persons
        ['SELECT', [Count('*')], 'FROM', persons]
        - columns: [Count('*')]
        - from: persons
        - table: persons
        db.persons.find.count(
        {},
        SON([]),
        )
        Results: (1)
        [{'count': 25}]
        SQLite Results: (1)
        [(25,)]

        >>> papy("select count(*) from persons where Age>25")
        select count(*) from persons where Age>25
        ['SELECT', [Count('*')], 'FROM', persons, 'WHERE', <Age > 25>]
        - columns: [Count('*')]
        - from: persons
        - table: persons
        - where_expr: <Age > 25>
        db.persons.find.count(
        {'Age': {'$gt': 25}},
        SON([]),
        )
        Results: (1)
        [{'count': 19}]
        SQLite Results: (1)
        [(19,)]
    """

def doctest_pypa_convert_ammsc():
    r"""
        >>> papy("select avg(persons.Age) from persons")
        select avg(persons.Age) from persons
        ['SELECT', [Avg(persons.Age)], 'FROM', persons]
        - columns: [Avg(persons.Age)]
        - from: persons
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': 'function(out) {\nout.AvgpersonsAge = out.sumfor_AvgpersonsAge / out.cntfor_AvgpersonsAge;\ndelete out.sumfor_AvgpersonsAge;\ndelete out.cntfor_AvgpersonsAge;\n}',
         'initial': {'AvgpersonsAge': 0,
                     'cntfor_AvgpersonsAge': 0,
                     'sumfor_AvgpersonsAge': 0},
         'key': None,
         'reduce': 'function(persons, out) {\nwith(persons) {out.sumfor_AvgpersonsAge += persons.Age;\nout.cntfor_AvgpersonsAge++;}\n}'}
        )
        Results: (1)
        [{u'AvgpersonsAge': 39.92}]
        SQLite Results: (1)
        [(39.92,)]

        >>> papy("select avg(Age) from persons", nodump=True)
        Results: (1)
        [{u'AvgAge': 39.92}]
        SQLite Results: (1)
        [(39.92,)]

        >>> papy("select avg(persons.Age+10) from persons")
        select avg(persons.Age+10) from persons
        ['SELECT', [Avg(persons.Age + 10)], 'FROM', persons]
        - columns: [Avg(persons.Age + 10)]
        - from: persons
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': 'function(out) {\nout.AvgpersonsAge = out.sumfor_AvgpersonsAge / out.cntfor_AvgpersonsAge;\ndelete out.sumfor_AvgpersonsAge;\ndelete out.cntfor_AvgpersonsAge;\n}',
         'initial': {'AvgpersonsAge': 0,
                     'cntfor_AvgpersonsAge': 0,
                     'sumfor_AvgpersonsAge': 0},
         'key': None,
         'reduce': 'function(persons, out) {\nwith(persons) {out.sumfor_AvgpersonsAge += persons.Age + 10;\nout.cntfor_AvgpersonsAge++;}\n}'}
        )
        Results: (1)
        [{u'AvgpersonsAge': 49.92}]
        SQLite Results: (1)
        [(49.92,)]

        >>> papy("select avg(Age+10) from persons", nodump=True)
        Results: (1)
        [{u'AvgAge': 49.92}]
        SQLite Results: (1)
        [(49.92,)]

    """

def doctest_pypa_convert_groupby():
    r"""
        >>> papy("select avg(Age) from persons group by Married")
        select avg(Age) from persons group by Married
        ['SELECT', [Avg(Age)], 'FROM', persons, 'GROUP', 'BY', [Married]]
        - columns: [Avg(Age)]
        - from: persons
        - group_by: ['GROUP', 'BY', [Married]]
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': 'function(out) {\nout.AvgAge = out.sumfor_AvgAge / out.cntfor_AvgAge;\ndelete out.sumfor_AvgAge;\ndelete out.cntfor_AvgAge;\n}',
         'initial': {'AvgAge': 0, 'cntfor_AvgAge': 0, 'sumfor_AvgAge': 0},
         'key': ['Married'],
         'reduce': 'function(persons, out) {\nwith(persons) {out.sumfor_AvgAge += Age;\nout.cntfor_AvgAge++;}\n}'}
        )
        Results: (2)
        [{u'AvgAge': 44.76923076923077, u'Married': True},
         {u'AvgAge': 34.666666666666664, u'Married': False}]
        SQLite Results: (2)
        [(34.666666666666664,), (44.76923076923077,)]

        >>> papy("select avg(persons.Age) from persons group by Married")
        select avg(persons.Age) from persons group by Married
        ['SELECT', [Avg(persons.Age)], 'FROM', persons, 'GROUP', 'BY', [Married]]
        - columns: [Avg(persons.Age)]
        - from: persons
        - group_by: ['GROUP', 'BY', [Married]]
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': 'function(out) {\nout.AvgpersonsAge = out.sumfor_AvgpersonsAge / out.cntfor_AvgpersonsAge;\ndelete out.sumfor_AvgpersonsAge;\ndelete out.cntfor_AvgpersonsAge;\n}',
         'initial': {'AvgpersonsAge': 0,
                     'cntfor_AvgpersonsAge': 0,
                     'sumfor_AvgpersonsAge': 0},
         'key': ['Married'],
         'reduce': 'function(persons, out) {\nwith(persons) {out.sumfor_AvgpersonsAge += persons.Age;\nout.cntfor_AvgpersonsAge++;}\n}'}
        )
        Results: (2)
        [{u'AvgpersonsAge': 44.76923076923077, u'Married': True},
         {u'AvgpersonsAge': 34.666666666666664, u'Married': False}]
        SQLite Results: (2)
        [(34.666666666666664,), (44.76923076923077,)]

        >>> papy("select Married, avg(persons.Age) from persons group by Married")
        select Married, avg(persons.Age) from persons group by Married
        ['SELECT', [Married, Avg(persons.Age)], 'FROM', persons, 'GROUP', 'BY', [Married]]
        - columns: [Married, Avg(persons.Age)]
        - from: persons
        - group_by: ['GROUP', 'BY', [Married]]
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': 'function(out) {\nout.AvgpersonsAge = out.sumfor_AvgpersonsAge / out.cntfor_AvgpersonsAge;\ndelete out.sumfor_AvgpersonsAge;\ndelete out.cntfor_AvgpersonsAge;\n}',
         'initial': {'AvgpersonsAge': 0,
                     'cntfor_AvgpersonsAge': 0,
                     'sumfor_AvgpersonsAge': 0},
         'key': ['Married'],
         'reduce': 'function(persons, out) {\nwith(persons) {out.Married = Married;\nout.sumfor_AvgpersonsAge += persons.Age;\nout.cntfor_AvgpersonsAge++;}\n}'}
        )
        Results: (2)
        [{u'AvgpersonsAge': 44.76923076923077, u'Married': True},
         {u'AvgpersonsAge': 34.666666666666664, u'Married': False}]
        SQLite Results: (2)
        [(0, 34.666666666666664), (1, 44.76923076923077)]

        >>> papy("select Married, avg(persons.Age) from persons group by 1")
        select Married, avg(persons.Age) from persons group by 1
        ['SELECT', [Married, Avg(persons.Age)], 'FROM', persons, 'GROUP', 'BY', [1]]
        - columns: [Married, Avg(persons.Age)]
        - from: persons
        - group_by: ['GROUP', 'BY', [1]]
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': 'function(out) {\nout.AvgpersonsAge = out.sumfor_AvgpersonsAge / out.cntfor_AvgpersonsAge;\ndelete out.sumfor_AvgpersonsAge;\ndelete out.cntfor_AvgpersonsAge;\n}',
         'initial': {'AvgpersonsAge': 0,
                     'cntfor_AvgpersonsAge': 0,
                     'sumfor_AvgpersonsAge': 0},
         'key': ['Married'],
         'reduce': 'function(persons, out) {\nwith(persons) {out.Married = Married;\nout.sumfor_AvgpersonsAge += persons.Age;\nout.cntfor_AvgpersonsAge++;}\n}'}
        )
        Results: (2)
        [{u'AvgpersonsAge': 44.76923076923077, u'Married': True},
         {u'AvgpersonsAge': 34.666666666666664, u'Married': False}]
        SQLite Results: (2)
        [(0, 34.666666666666664), (1, 44.76923076923077)]

        >>> papy("select Married, avg(persons.Age) from persons group by persons.Married")
        select Married, avg(persons.Age) from persons group by persons.Married
        ['SELECT', [Married, Avg(persons.Age)], 'FROM', persons, 'GROUP', 'BY', [persons.Married]]
        - columns: [Married, Avg(persons.Age)]
        - from: persons
        - group_by: ['GROUP', 'BY', [persons.Married]]
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': 'function(out) {\nout.AvgpersonsAge = out.sumfor_AvgpersonsAge / out.cntfor_AvgpersonsAge;\ndelete out.sumfor_AvgpersonsAge;\ndelete out.cntfor_AvgpersonsAge;\n}',
         'initial': {'AvgpersonsAge': 0,
                     'cntfor_AvgpersonsAge': 0,
                     'sumfor_AvgpersonsAge': 0},
         'key': ['Married'],
         'reduce': 'function(persons, out) {\nwith(persons) {out.Married = Married;\nout.sumfor_AvgpersonsAge += persons.Age;\nout.cntfor_AvgpersonsAge++;}\n}'}
        )
        Results: (2)
        [{u'AvgpersonsAge': 44.76923076923077, u'Married': True},
         {u'AvgpersonsAge': 34.666666666666664, u'Married': False}]
        SQLite Results: (2)
        [(0, 34.666666666666664), (1, 44.76923076923077)]

        >>> papy("select persons.FirstName+persons.LastName, avg(persons.Age) from persons group by 1")
        select persons.FirstName+persons.LastName, avg(persons.Age) from persons group by 1
        ['SELECT', [persons.FirstName + persons.LastName, Avg(persons.Age)], 'FROM', persons, 'GROUP', 'BY', [1]]
        - columns: [persons.FirstName + persons.LastName, Avg(persons.Age)]
        - from: persons
        - group_by: ['GROUP', 'BY', [1]]
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': 'function(out) {\nout.AvgpersonsAge = out.sumfor_AvgpersonsAge / out.cntfor_AvgpersonsAge;\ndelete out.sumfor_AvgpersonsAge;\ndelete out.cntfor_AvgpersonsAge;\n}',
         'initial': {'AvgpersonsAge': 0,
                     'cntfor_AvgpersonsAge': 0,
                     'sumfor_AvgpersonsAge': 0},
         'key': 'function(persons) {\nwith(persons) {return {personsFirstNamepersonsLastName : persons.personsFirstNamepersonsLastName}\n}}',
         'reduce': 'function(persons, out) {\nwith(persons) {out.personsFirstNamepersonsLastName = persons.FirstName + persons.LastName;\nout.sumfor_AvgpersonsAge += persons.Age;\nout.cntfor_AvgpersonsAge++;}\n}'}
        )
        Results: (1)
        [{u'AvgpersonsAge': 39.92,
          u'personsFirstNamepersonsLastName': u'HaleyRocheford'}]
        SQLite Results: (1)
        [(0, 39.92)]

        >>> papy("select persons.FirstName+persons.LastName, avg(persons.Age) from persons group by persons.FirstName+persons.LastName")
        select persons.FirstName+persons.LastName, avg(persons.Age) from persons group by persons.FirstName+persons.LastName
        ['SELECT', [persons.FirstName + persons.LastName, Avg(persons.Age)], 'FROM', persons, 'GROUP', 'BY', [persons.FirstName + persons.LastName]]
        - columns: [persons.FirstName + persons.LastName, Avg(persons.Age)]
        - from: persons
        - group_by: ['GROUP', 'BY', [persons.FirstName + persons.LastName]]
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': 'function(out) {\nout.AvgpersonsAge = out.sumfor_AvgpersonsAge / out.cntfor_AvgpersonsAge;\ndelete out.sumfor_AvgpersonsAge;\ndelete out.cntfor_AvgpersonsAge;\n}',
         'initial': {'AvgpersonsAge': 0,
                     'cntfor_AvgpersonsAge': 0,
                     'sumfor_AvgpersonsAge': 0},
         'key': 'function(persons) {\nwith(persons) {return {personsFirstNamepersonsLastName : persons.personsFirstNamepersonsLastName}\n}}',
         'reduce': 'function(persons, out) {\nwith(persons) {out.personsFirstNamepersonsLastName = persons.FirstName + persons.LastName;\nout.sumfor_AvgpersonsAge += persons.Age;\nout.cntfor_AvgpersonsAge++;}\n}'}
        )
        Results: (1)
        [{u'AvgpersonsAge': 39.92,
          u'personsFirstNamepersonsLastName': u'HaleyRocheford'}]
        SQLite Results: (1)
        [(0, 39.92)]

        >>> papy("select FirstName+LastName, avg(persons.Age) from persons group by 1",
        ...     nodump=True)
        Results: (1)
        [{u'AvgpersonsAge': 39.92, u'FirstNameLastName': u'HaleyRocheford'}]
        SQLite Results: (1)
        [(0, 39.92)]

        >>> papy("select FirstName+LastName, avg(persons.Age) from persons group by FirstName+LastName",
        ...     nodump=True)
        Results: (1)
        [{u'AvgpersonsAge': 39.92, u'FirstNameLastName': u'HaleyRocheford'}]
        SQLite Results: (1)
        [(0, 39.92)]


        >>> papy("select FirstName+LastName as name, avg(persons.Age) from persons group by name")
        select FirstName+LastName as name, avg(persons.Age) from persons group by name
        ['SELECT', [FirstName + LastName AS name, Avg(persons.Age)], 'FROM', persons, 'GROUP', 'BY', [name]]
        - columns: [FirstName + LastName AS name, Avg(persons.Age)]
        - from: persons
        - group_by: ['GROUP', 'BY', [name]]
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': 'function(out) {\nout.AvgpersonsAge = out.sumfor_AvgpersonsAge / out.cntfor_AvgpersonsAge;\ndelete out.sumfor_AvgpersonsAge;\ndelete out.cntfor_AvgpersonsAge;\n}',
         'initial': {'AvgpersonsAge': 0,
                     'cntfor_AvgpersonsAge': 0,
                     'sumfor_AvgpersonsAge': 0},
         'key': ['name'],
         'reduce': 'function(persons, out) {\nwith(persons) {out.name = FirstName + LastName;\nout.sumfor_AvgpersonsAge += persons.Age;\nout.cntfor_AvgpersonsAge++;}\n}'}
        )
        Results: (1)
        [{u'AvgpersonsAge': 39.92, u'name': u'HaleyRocheford'}]
        SQLite Results: (1)
        [(0, 39.92)]


    """

def doctest_Query_exprToDict():
    """
        >>> q = tomongo.Query()

        >>> def t(expr):
        ...     p = select_parser.expr.parseString(expr)
        ...     print p
        ...     pprint(tomongo.exprToDict(p[0], q))

        >>> t('Age = 18')
        [<Age = 18>]
        {'Age': 18}

        >>> t('Age < 18')
        [<Age < 18>]
        {'Age': {'$lt': 18}}

        >>> t("FirstName = 'Agnes'")
        [<FirstName = Agnes>]
        {'FirstName': 'Agnes'}

        >>> t("Age = 18 AND FirstName = 'Agnes'")
        [AND [<Age = 18>, <FirstName = Agnes>]]
        {'$and': [{'Age': 18}, {'FirstName': 'Agnes'}]}

        >>> t("Age = 18 AND FirstName = 'Agnes' AND LastName = 'Meyer'")
        [AND [<Age = 18>, <FirstName = Agnes>, <LastName = Meyer>]]
        {'$and': [{'Age': 18}, {'FirstName': 'Agnes'}, {'LastName': 'Meyer'}]}

        >>> t("Age > 18 AND FirstName = 'Agnes' AND LastName = 'Meyer'")
        [AND [<Age > 18>, <FirstName = Agnes>, <LastName = Meyer>]]
        {'$and': [{'Age': {'$gt': 18}}, {'FirstName': 'Agnes'}, {'LastName': 'Meyer'}]}

        >>> t("Age > 18 OR FirstName = 'Agnes' AND LastName = 'Meyer'")
        [OR [<Age > 18>, AND [<FirstName = Agnes>, <LastName = Meyer>]]]
        {'$or': [{'Age': {'$gt': 18}},
                 {'$and': [{'FirstName': 'Agnes'}, {'LastName': 'Meyer'}]}]}

        >>> t("Age > 18 OR (FirstName = 'Agnes' AND LastName = 'Meyer')")
        [OR [<Age > 18>, AND [<FirstName = Agnes>, <LastName = Meyer>]]]
        {'$or': [{'Age': {'$gt': 18}},
                 {'$and': [{'FirstName': 'Agnes'}, {'LastName': 'Meyer'}]}]}

        >>> t("(Age > 18 OR FirstName = 'Agnes') AND LastName = 'Meyer')")
        [AND [OR [<Age > 18>, <FirstName = Agnes>], <LastName = Meyer>]]
        {'$and': [{'$or': [{'Age': {'$gt': 18}}, {'FirstName': 'Agnes'}]},
                  {'LastName': 'Meyer'}]}
    """

def doctest_pypa_convert_with_expr():
    r"""
        >>> papy("select LastName, id+Age from persons")
        select LastName, id+Age from persons
        ['SELECT', [LastName, id + Age], 'FROM', persons]
        - columns: [LastName, id + Age]
        - from: persons
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': None,
         'initial': {},
         'key': ['_id'],
         'reduce': 'function(persons, out) {\nwith(persons) {out.LastName = LastName;\nout.idAge = id + Age;}\n}'}
        )
        Results: (25)
        [{u'LastName': u'Vaill',
          u'_id': ObjectId('516660fcba81c5021d74cd48'),
          u'idAge': 36.0},
         {u'LastName': u'Roudabush',
          u'_id': ObjectId('516660fcba81c5021d74cd49'),
          u'idAge': 64.0},
         {u'LastName': u'Tinnes',
          u'_id': ObjectId('516660fcba81c5021d74cd4a'),
          u'idAge': 54.0},
         {u'LastName': u'Mockus',
          u'_id': ObjectId('516660fcba81c5021d74cd4b'),
          u'idAge': 74.0},
         {u'LastName': u'Fifield',
          u'_id': ObjectId('516660fcba81c5021d74cd4c'),
          u'idAge': 74.0},
         {u'LastName': u'Laboy',
          u'_id': ObjectId('516660fcba81c5021d74cd4d'),
          u'idAge': 32.0},
         {u'LastName': u'Haakinson',
          u'_id': ObjectId('516660fcba81c5021d74cd4e'),
          u'idAge': 27.0},
         {u'LastName': u'Pou',
          u'_id': ObjectId('516660fcba81c5021d74cd4f'),
          u'idAge': 28.0},
         {u'LastName': u'Hasty',
          u'_id': ObjectId('516660fcba81c5021d74cd50'),
          u'idAge': 55.0},
         {u'LastName': u'Earman',
          u'_id': ObjectId('516660fcba81c5021d74cd51'),
          u'idAge': 56.0},
         {u'LastName': u'Dragaj',
          u'_id': ObjectId('516660fcba81c5021d74cd52'),
          u'idAge': 41.0},
         {u'LastName': u'Mcdonnell',
          u'_id': ObjectId('516660fcba81c5021d74cd53'),
          u'idAge': 65.0},
         {u'LastName': u'Lanfear',
          u'_id': ObjectId('516660fcba81c5021d74cd54'),
          u'idAge': 57.0},
         {u'LastName': u'Behen',
          u'_id': ObjectId('516660fcba81c5021d74cd55'),
          u'idAge': 81.0},
         {u'LastName': u'Groden',
          u'_id': ObjectId('516660fcba81c5021d74cd56'),
          u'idAge': 42.0},
         {u'LastName': u'Krenzke',
          u'_id': ObjectId('516660fcba81c5021d74cd57'),
          u'idAge': 34.0},
         {u'LastName': u'Brevard',
          u'_id': ObjectId('516660fcba81c5021d74cd58'),
          u'idAge': 35.0},
         {u'LastName': u'Reich',
          u'_id': ObjectId('516660fcba81c5021d74cd59'),
          u'idAge': 65.0},
         {u'LastName': u'Worlds',
          u'_id': ObjectId('516660fcba81c5021d74cd5a'),
          u'idAge': 37.0},
         {u'LastName': u'Inafuku',
          u'_id': ObjectId('516660fcba81c5021d74cd5b'),
          u'idAge': 51.0},
         {u'LastName': u'Loose',
          u'_id': ObjectId('516660fcba81c5021d74cd5c'),
          u'idAge': 55.0},
         {u'LastName': u'Pindell',
          u'_id': ObjectId('516660fcba81c5021d74cd5d'),
          u'idAge': 42.0},
         {u'LastName': u'Sharper',
          u'_id': ObjectId('516660fcba81c5021d74cd5e'),
          u'idAge': 51.0},
         {u'LastName': u'Mccamey',
          u'_id': ObjectId('516660fcba81c5021d74cd5f'),
          u'idAge': 74.0},
         {u'LastName': u'Rocheford',
          u'_id': ObjectId('516660fcba81c5021d74cd60'),
          u'idAge': 93.0}]
        SQLite Results: (25)
        [(u'Vaill', 36),
         (u'Roudabush', 64),
         (u'Tinnes', 54),
         (u'Mockus', 74),
         (u'Fifield', 74),
         (u'Laboy', 32),
         (u'Haakinson', 27),
         (u'Pou', 28),
         (u'Hasty', 55),
         (u'Earman', 56),
         (u'Dragaj', 41),
         (u'Mcdonnell', 65),
         (u'Lanfear', 57),
         (u'Behen', 81),
         (u'Groden', 42),
         (u'Krenzke', 34),
         (u'Brevard', 35),
         (u'Reich', 65),
         (u'Worlds', 37),
         (u'Inafuku', 51),
         (u'Loose', 55),
         (u'Pindell', 42),
         (u'Sharper', 51),
         (u'Mccamey', 74),
         (u'Rocheford', 93)]
    """


def doctest_pypa_convert_with_as():
    r"""
    Oh well, we don't rewrite column names is simple queries

        >>> papy("select LastName as foo from persons")
        select LastName as foo from persons
        ['SELECT', [LastName AS foo], 'FROM', persons]
        - columns: [LastName AS foo]
        - from: persons
        - table: persons
        db.persons.find(
        {},
        SON([('_id', 0), ('LastName', 1)]),
        )
        Results: (25)
        [{u'LastName': u'Vaill'},
        ...

        >>> papy("select LastName as foo, id+Age as bar from persons")
        select LastName as foo, id+Age as bar from persons
        ['SELECT', [LastName AS foo, id + Age AS bar], 'FROM', persons]
        - columns: [LastName AS foo, id + Age AS bar]
        - from: persons
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': None,
         'initial': {},
         'key': ['_id'],
         'reduce': 'function(persons, out) {\nwith(persons) {out.foo = LastName;\nout.bar = id + Age;}\n}'}
        )
        Results: (25)
        [{u'_id': ObjectId('516660fcba81c5021d74cd48'),
          u'bar': 36.0,
          u'foo': u'Vaill'},
        ...
    """


def doctest_pypa_convert_with_sqlresults():
    r"""
        >>> papy("select LastName, id+Age from persons", sqlresults=True)
        select LastName, id+Age from persons
        ['SELECT', [LastName, id + Age], 'FROM', persons]
        - columns: [LastName, id + Age]
        - from: persons
        - table: persons
        db.persons.group(
        {'condition': {},
         'finalize': None,
         'initial': {},
         'key': ['_id'],
         'reduce': 'function(persons, out) {\nwith(persons) {out.LastName = LastName;\nout.idAge = id + Age;}\n}'}
        )
        Results: (25)
        [(u'Vaill', 36.0),
         (u'Roudabush', 64.0),
         (u'Tinnes', 54.0),
         (u'Mockus', 74.0),
         (u'Fifield', 74.0),
         (u'Laboy', 32.0),
         (u'Haakinson', 27.0),
         (u'Pou', 28.0),
         (u'Hasty', 55.0),
         (u'Earman', 56.0),
         (u'Dragaj', 41.0),
         (u'Mcdonnell', 65.0),
         (u'Lanfear', 57.0),
         (u'Behen', 81.0),
         (u'Groden', 42.0),
         (u'Krenzke', 34.0),
         (u'Brevard', 35.0),
         (u'Reich', 65.0),
         (u'Worlds', 37.0),
         (u'Inafuku', 51.0),
         (u'Loose', 55.0),
         (u'Pindell', 42.0),
         (u'Sharper', 51.0),
         (u'Mccamey', 74.0),
         (u'Rocheford', 93.0)]
        SQLite Results: (25)
        [(u'Vaill', 36),
         (u'Roudabush', 64),
         (u'Tinnes', 54),
         (u'Mockus', 74),
         (u'Fifield', 74),
         (u'Laboy', 32),
         (u'Haakinson', 27),
         (u'Pou', 28),
         (u'Hasty', 55),
         (u'Earman', 56),
         (u'Dragaj', 41),
         (u'Mcdonnell', 65),
         (u'Lanfear', 57),
         (u'Behen', 81),
         (u'Groden', 42),
         (u'Krenzke', 34),
         (u'Brevard', 35),
         (u'Reich', 65),
         (u'Worlds', 37),
         (u'Inafuku', 51),
         (u'Loose', 55),
         (u'Pindell', 42),
         (u'Sharper', 51),
         (u'Mccamey', 74),
         (u'Rocheford', 93)]
    """

#def doctest_pypa_convert_with_expr_orderby():
#    r"""
#        >>> papy("select LastName, id+Age from persons order by 1")
#        select LastName, id+Age from persons order by 1
#        ['SELECT', [LastName, id + Age], 'FROM', persons, 'ORDER', 'BY', [[1]]]
#        - columns: [LastName, id + Age]
#        - from: persons
#        - order_by_terms: [[1]]
#        - table: persons
#        db.persons.group(
#        {'condition': {},
#         'finalize': None,
#         'initial': {},
#         'key': ['_id'],
#         'reduce': 'function(persons, out) {\nwith(persons) {out.LastName = LastName;\nout.idAge = id + Age;}\n}'}
#        )
#        Results: (25)
#        ...
#
#        >>> papy("select LastName, id+Age from persons order by 1,2")
#    """

def doctest_pypa_compare():
    r"""
        >>> papy_compare("select LastName, id+Age from persons")
    """


def doctest_pypa_where_nonconst():
    r"""

    NO-GO:

        >>> papy("select FirstName from persons where Age<id")
        Traceback (most recent call last):
        ...
        Unsupported: Mongo only supports comparison with a constant, not field to field
    """


def doctest_exprToName():
    r"""

        >>> o =tomongo.Query()

        >>> print o.exprToName("FirstName")
        FirstName

        >>> print o.exprToName("avg(Age)")
        avgAge

        >>> print o.exprToName("avg(Age)")
        avgAge

        >>> print o.exprToName("avg(age)")
        avgage

        >>> print o.exprToName("avg((Age))")
        avgAge_1

        >>> print o.exprToName("avg(Age)")
        avgAge

        >>> print o.exprToName("persons.FirstName+persons.LastName")
        personsFirstNamepersonsLastName

        >>> print o.exprToName("persons.FirstName+persons.LastName")
        personsFirstNamepersonsLastName

    """


def setUp(test):
    make_test_db()


def tearDown(test):
    pass


def test_suite():
    return doctest.DocTestSuite(
        setUp=setUp, tearDown=tearDown,
        checker=checker,
        optionflags=testing.DOCTEST_OPTION_FLAGS)
