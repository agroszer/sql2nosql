# convert a parsed SQL to mongo query
import string
from pprint import pformat
from bson import son
from sql2nosql import select_parser


class ConversionError(Exception):
    pass


class Unsupported(Exception):
    pass

#TODO:
# count(distinct patient_hash)
# ditch unneeded output, like group key in results
# basic create+insert -> run sqlite3 tests
# eventually switch all that crap to aggregation framework or map-reduce
# http://docs.mongodb.org/manual/reference/sql-aggregation-comparison/
# http://www.infoq.com/articles/implementing-aggregation-functions-in-mongodb

#Comparison
#    $all
#    $gt
#    $gte
#    $in
#    $lt
#    $lte
#    $ne
#    $nin
#Logical
#    $and
#    $nor
#    $not
#    $or
#Element
#    $exists
#    $mod
#    $type
#JavaScript
#    $regex
#    $where
#Geospatial Operators:
#    $geoWithin
#    $geoIntersects
#    $near
#    $nearSphere
#Parameters:
#    $geometry
#    $maxDistance
#    $center
#    $centerSphere
#    $box
#    $polygon
#    $uniqueDocs
#Array
#    $elemMatch
#    $size

OPS = {'<': '$lt',
       '>': '$gt',
       '<=': '$lte',
       '>=': '$gte',
       '!=': '$ne',
       '<>': '$ne',
       }


class Node(object):
    translateAttributes = ()

    def __init__(self, ast):
        self._ast = ast
        for a in self.translateAttributes:
            v = getattr(ast, a)
            v = translate(v)
            setattr(self, a, v)

    def __getattr__(self, name):
        # mirror select_parser ast attributes
        return getattr(self._ast, name)

    def __repr__(self):
        return repr(self._ast)


class Comparison(Node):
    translateAttributes = ('lh', 'rh')

    def mongo(self, query, name=None):
        if isinstance(self.lh, Identifier) and isinstance(self.rh, Identifier):
            raise Unsupported("Mongo only supports comparison with a constant, not field to field")

        if not isinstance(self.lh, Identifier):
            raise Unsupported("Mongo only supports comparison with a field on LH")
        if not isinstance(self.rh, (basestring, int, long)):
            raise Unsupported("Mongo only supports comparison with a constant on RH")
        lh = str(self.lh)

        if self.op == '=' or self.op == '==':
            return {lh: self.rh}
        elif self.op == 'in':
            return {lh: {'$in': self.rh}}
        else:
            # XXX: turn around if it's 18 < Age
            return {lh: {OPS[self.op]: self.rh}}

class Between(Node):
    #translateAttributes = ('expr', 'lower', 'upper')

    def mongo(self, query, name=None):
        op1 = Comparison(select_parser.Comparison(self._ast.lower, '<=', self._ast.expr))
        op2 = Comparison(select_parser.Comparison(self._ast.expr, '<=', self._ast.upper))
        return {'$and': [op1.mongo(query, name),
                         op2.mongo(query, name)]}

class And(Node):
    def mongo(self, query, name=None):
        return {'$and': [exprToDict(e, query) for e in self.args]}


class Or(Node):
    def mongo(self, query, name=None):
        return {'$or': [exprToDict(e, query) for e in self.args]}


def exprToDict(expr, query):
    try:
        t = translate(expr)
        rv = t.mongo(query)
        return rv
    except AttributeError:
        from dbgp.client import brk; brk('127.0.0.1')


class AmmscNode(Node):
    pass

class Count(AmmscNode):
    def mongoName(self, query):
        name = "count_%s" % query.exprToName(self.expr)
        return name

    def mongo(self, query, name=None):
        if name is None:
            name = self.mongoName(query)
        query.groupOptions['initial'][name] = 0
        query.groupOptions['reduce'].append("%s++" % name)


class Avg(AmmscNode):
    def mongoName(self, query):
        name = "avg_%s" % query.exprToName(self.expr)
        return name

    def mongo(self, query, name=None):
        if name is None:
            name = self.mongoName(query)
        query.groupOptions['initial'][name] = 0
        query.groupOptions['initial']['sumfor_%s' % name] = 0
        query.groupOptions['initial']['cntfor_%s' % name] = 0
        query.groupOptions['reduce'].append(
            "out.sumfor_%s += %s;" % (name, self.expr))
        query.groupOptions['reduce'].append(
            "out.cntfor_%s++;" % (name, ))
        query.groupOptions['finalize'].append(
            "out.%s = out.sumfor_%s / out.cntfor_%s;" % (name, name, name))
        query.groupOptions['finalize'].append(
            "delete out.sumfor_%s;" % (name, ))
        query.groupOptions['finalize'].append(
            "delete out.cntfor_%s;" % (name, ))


class Sum(AmmscNode):
    pass


class Min(AmmscNode):
    pass


class Max(AmmscNode):
    pass


class Expr(Node):
    pass


class BinaryExpr(Expr):
    def mongoName(self, query):
        expr = str(self._ast)
        name = query.exprToName(expr)
        return name

    def mongo(self, query, name=None):
        if name is None:
            name = self.mongoName(query)
        expr = str(self._ast)

        query.groupOptions['reduce'].append(
            "out.%s = %s;" % (name, expr))


class Identifier(Node):
    def mongoName(self, query):
        return self._ast

    def mongo(self, query, name=None):
        if name is None:
            name = self.mongoName(query)
        expr = str(self._ast)

        try:
            query.groupOptions['reduce'].append(
                "out.%s = %s;" % (name, expr))
        except:
            from dbgp.client import brk; brk('127.0.0.1')

    def __repr__(self):
        return str(self._ast)


class Column(Node):
    translateAttributes = ('expr',)
    _mongoName = None

    def mongoName(self, query):
        if self._ast.alias:
            return self._ast.alias
        if self._mongoName is None:
            self._mongoName = query.exprToName(self.expr)
        return self._mongoName

    def mongo(self, query, name=None):
        #expr = str(self.expr)
        name = self.mongoName(query)
        self.expr.mongo(query, name)

        #query.groupOptions['reduce'].append(
        #    "out.%s = %s;" % (name, expr))

    def haveExpr(self):
        return isinstance(self.expr, Expr)

    def __repr__(self):
        return str(self.expr)


def makeInt(e):
    return e

def makeStr(e):
    return e

PARSER_AST_TO_MONGO = {
    select_parser.Comparison: Comparison,
    select_parser.And: And,
    select_parser.Or: Or,
    select_parser.Count: Count,
    select_parser.Avg: Avg,
    #select_parser.Min: Min,
    #select_parser.Max: Max,
    #select_parser.Sum: Sum,
    select_parser.BinaryExpr: BinaryExpr,
    select_parser.Column: Column,
    select_parser.Identifier: Identifier,
    select_parser.Between: Between,
    #str: Name,  # whatever name sofar
    int: makeInt,
    str: makeStr,
}


def translate(expr):
    if isinstance(expr, list):
        rv = []
        for e in expr:
            rv.append(translate(e))
        return rv
    else:
        return PARSER_AST_TO_MONGO[expr.__class__](expr)


class Query(object):
    counter = 0  # a counter for expr -> column names
    expr2name = None
    name2expr = None

    def __init__(self, sql=None):
        self.expr2name = {}
        self.name2expr = {}

        if sql:
            self.prepare(sql)

    def doWhere(self):
        self.spec = {}
        if 'where_expr' in self.parsed:
            self.spec = exprToDict(self.parsed.where_expr, self)

    def doFrom(self):
        if not 'from' in self.parsed:
            raise ConversionError("Please specify one table in FROM")
        frm = translate(self.parsed['from'])
        if isinstance(frm, Identifier):
            frm = [frm]

        if len(frm) != 1:
            raise ConversionError("Just one table supported in FROM")

        self.collection = str(frm[0])

    def haveExpr(self, columns):
        for c in columns:
            if c.haveExpr():
                return True
        return False

    def findAmmsc(self, presult):
        rv = []
        for i in presult:
            if isinstance(i.expr, AmmscNode):
                rv.append(i)
        return rv

    def prepare(self, sql):
        self.sql = sql
        self.parsed = parsed = select_parser.select_stmt.parseString(sql)
        self.groupOptions = None

        self.doFrom()
        self.doWhere()

        columns = list(select_parser.flatten(parsed.columns.asList()))
        columns = translate(columns)
        self.columns = columns

        # look for evtl. count/avg/etc for grouping
        ammscs = self.findAmmsc(columns)
        if not ammscs and not self.haveExpr(columns):
            # no grouping function, as simple as it gets
            self.command = 'find'
            self.fields = son.SON({'_id': 0})
            if len(columns) == 1 and str(columns[0].expr) == '*':
                pass
            else:
                # field order should matter, but is not respected by mongo
                for c in columns:
                    self.fields[self.mangleColumnName(str(c))] = 1
        else:
            # a bit more complex

            # corner case:
            # select count(*) from ... (opt where)
            if (len(columns) == 1 and len(ammscs) == 1
                and str(ammscs[0].expr) == "Count('*')"):
                self.command = 'find.count'
                self.fields = son.SON({})
            # corner case:
            # select count(distinct field) from ... (opt where)
            #elif if (len(columns) and len(ammscs) == 1
            #    and isinstance(ammscs[0], select_parser.Count)
            #    and ammscs[0].expr == '*'):
            #    self.command = 'find.distinct.count'
            #    self.fields = son.SON({})
            else:
                self.command = 'group'
                self.groupOptions = dict(initial={},
                                         reduce=[], finalize=[])

                for c in columns:
                    c.mongo(self)

                if 'group_by' in parsed:
                    keys = []
                    haveExpr = False
                    for idx, k in enumerate(
                        select_parser.flatten(parsed.group_by[2].asList())):
                        k = translate(k)
                        if isinstance(k, Identifier):
                            # simple field name
                            keys.append(self.mangleColumnName(str(k)))
                        elif isinstance(k, (int, long)):
                            # column index
                            cname = self.mangleColumnName(columns[k-1].expr)
                            if isinstance(cname, Identifier):
                                # just a column name
                                keys.append(str(cname))
                            else:
                                # or expr???
                                keys.append(columns[idx].mongoName(self))
                                haveExpr = True
                        else:
                            # huhh? maybe expr?
                            keys.append(k.mongoName(self))
                            haveExpr = True
                    if haveExpr:
                        keys = ["%s : %s.%s" % (k, self.collection, k)
                                for idx, k in enumerate(keys)]
                        # JS `with`: a way to make the document attributes available
                        # as "local" variables, to have expressions working without
                        # the collection prefix
                        keys = 'function(%s) {\nwith(%s) {return {%s}\n}}' % (
                                self.collection, self.collection, ', '.join(keys))

                else:
                    if len(ammscs) > 0:
                        keys = None
                    else:
                        # ohh well, this is a corner case when ONLY
                        # expressions are in the select columns
                        # I don't have a better idea then group by _id
                        # and output the expression results by reduce
                        keys = ['_id']

                self.groupOptions['key'] = keys
                # JS `with`: a way to make the document attributes available
                # as "local" variables, to have expressions working without
                # the collection prefix
                self.groupOptions['reduce'] = 'function(%s, out) {\nwith(%s) {%s}\n}' % (
                    self.collection, self.collection,
                    '\n'.join(self.groupOptions['reduce']))
                if self.groupOptions['finalize']:
                    self.groupOptions['finalize'] = 'function(out) {\n%s\n}' % (
                        '\n'.join(self.groupOptions['finalize']), )
                else:
                    self.groupOptions['finalize'] = None
                self.groupOptions['condition'] = self.spec

        self.limit = None
        self.skip = None

    def mangleColumnName(self, cname):
        try:
            if cname.startswith(self.collection + '.'):
                cname = cname[len(self.collection + '.'):]
        except AttributeError:
            # XXX:
            pass
        return cname

    def exprToName(self, expr):
        sexpr = str(expr)
        try:
            return self.expr2name[sexpr]
        except KeyError:
            pass

        rv = ''
        for i in sexpr:  # a very dirty way to make anything a string
            if i in string.ascii_letters:
                rv += i
        if len(rv) < len(str(expr)):
            cnt = self.name2expr.get(rv, 0)
            if cnt > 0:
                rv += '_' + str(cnt)
            self.name2expr[rv] = cnt + 1

        self.expr2name[sexpr] = rv
        return rv

    def dump(self):
        out = []
        out.append(self.sql)
        out.append(self.parsed.dump())
        if 'find' in self.command:
            out.append("db.%s.%s(" % (self.collection, self.command))
            out.append(pformat(self.spec)+",")
            out.append(pformat(self.fields)+",")
            out.append(")")
        elif self.command == 'group':
            out.append("db.%s.%s(" % (self.collection, self.command))
            out.append(pformat(self.groupOptions))
            out.append(")")

        return '\n'.join(out)

    def doFind(self, collection):
        kw = dict(spec=self.spec, fields=self.fields)
        if self.limit:
            kw['limit'] = self.limit
        if self.skip:
            kw['skip'] = self.skip
        return collection.find(**kw)

    def execute(self, db, params=None):
        collection = db[self.collection]
        res = None
        if self.command == 'find':
            res = self.doFind(collection)
        elif self.command == 'find.count':
            res = self.doFind(collection)
            res = [{'count': res.count()}]  # emulate a table
        elif self.command == 'group':
            res = collection.group(**self.groupOptions)
            # XXX: needs sorting!
            if 'order by' in self.sql.lower():
                raise Unsupported("Need to implement local sorting for this")
        return res

    def sqlresults(self, res):
        for row in res:
            out = tuple([row[c.mongoName(self)] for c in self.columns])
            yield out
