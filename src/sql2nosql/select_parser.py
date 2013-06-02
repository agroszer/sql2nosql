# select_parser.py
# Copyright 2010, Paul McGuire
# Modified 2013 by Adam Groszer
#          started on adding AST like classes
#          still needs a LOT of adjustment to be fully ANSI SQL compliant
#
# a simple SELECT statement parser, taken from SQLite's SELECT statement
# definition at http://www.sqlite.org/lang_select.html
#
import collections
from pyparsing import *
ParserElement.enablePackrat()

LPAR, RPAR, COMMA = map(Suppress, "(),")
#COMMA = Suppress(",")
#LPAR = Literal("(")
#RPAR = Literal(")")
select_stmt = Forward().setName("select statement")

# keywords
(UNION, ALL, AND, INTERSECT, EXCEPT, COLLATE, ASC, DESC, ON, USING, NATURAL, INNER,
    CROSS, LEFT, OUTER, JOIN, AS, INDEXED, NOT, SELECT, DISTINCT, FROM, WHERE, GROUP, BY,
    HAVING, ORDER, BY, LIMIT, OFFSET, OR, COUNT, AVG,
    CREATE, TABLE, INSERT, INTO, VALUES) = map(
    CaselessKeyword, """UNION, ALL, AND, INTERSECT,
 EXCEPT, COLLATE, ASC, DESC, ON, USING, NATURAL, INNER, CROSS, LEFT, OUTER, JOIN, AS, INDEXED, NOT, SELECT,
 DISTINCT, FROM, WHERE, GROUP, BY, HAVING, ORDER, BY, LIMIT, OFFSET, OR, COUNT, AVG,
 CREATE, TABLE, INSERT, INTO, VALUES""".replace(",", "").split())
(CAST, ISNULL, NOTNULL, NULL, IS, BETWEEN, ELSE, END, CASE, WHEN, THEN, EXISTS,
 COLLATE, IN, LIKE, GLOB, REGEXP, MATCH, ESCAPE, CURRENT_TIME, CURRENT_DATE,
 CURRENT_TIMESTAMP) = map(CaselessKeyword, """CAST, ISNULL, NOTNULL, NULL, IS, BETWEEN, ELSE,
 END, CASE, WHEN, THEN, EXISTS, COLLATE, IN, LIKE, GLOB, REGEXP, MATCH, ESCAPE,
 CURRENT_TIME, CURRENT_DATE, CURRENT_TIMESTAMP""".replace(",", "").split())
keyword = MatchFirst((
    UNION, ALL, INTERSECT, EXCEPT, COLLATE, ASC, DESC, ON, USING, NATURAL, INNER,
    CROSS, LEFT, OUTER, JOIN, AS, INDEXED, NOT, SELECT, DISTINCT, FROM, WHERE, GROUP, BY,
    HAVING, ORDER, BY, LIMIT, OFFSET, CAST, ISNULL, NOTNULL, NULL, IS, BETWEEN, ELSE, END, CASE, WHEN, THEN, EXISTS,
    COLLATE, IN, LIKE, GLOB, REGEXP, MATCH, ESCAPE, CURRENT_TIME, CURRENT_DATE,
    CURRENT_TIMESTAMP))

class Node(object):
    pass

class Identifier(Node):
    def __init__(self, identifier):
        self.identifier = identifier

    def __repr__(self):
        return self.identifier

def convertIdent(s, l, toks):
    return Identifier(toks.asList()[0])

identifier = ~keyword + Word(alphas, alphanums+"_")
identifier.setParseAction(convertIdent)
collation_name = identifier.copy()
column_name = identifier.copy()
column_alias = identifier.copy()
db_name = identifier.copy()
table_name = identifier.copy()
table_alias = identifier.copy()
index_name = identifier.copy()
function_name = identifier.copy()
parameter_name = identifier.copy()
database_name = identifier.copy()

# expression
expr = Forward().setName("expression")

def convertNumbers(s, l, toks):
    n = toks[0]
    try:
        return int(n)
    except ValueError:
        return float(n)

#integer = Regex(r"[+-]?\d+")
numeric_literal = Regex(r"\d+(\.\d*)?([eE][+-]?\d+)?")
numeric_literal.setParseAction(convertNumbers)
string_literal = QuotedString("'")
#string_literal.setParseAction(convertString)
blob_literal = Regex(r"[xX]'[0-9A-Fa-f]+'")
literal_value = ( numeric_literal | string_literal | blob_literal |
    NULL | CURRENT_TIME | CURRENT_DATE | CURRENT_TIMESTAMP )
bind_parameter = (
    Word("?", nums) |
    Combine(oneOf(": @ $") + parameter_name)
    )
type_name = oneOf("TEXT REAL INTEGER BLOB NULL")

class And(Node):
    def __init__(self, args):
        self.args = args
    def __repr__(self):
        return "AND %r" % self.args
        #return "<" + " AND ".join(["%r" % a for a in self.args]) + ">"

class Or(Node):
    def __init__(self, args):
        self.args = args
    def __repr__(self):
        return "OR %r" % self.args
        #return "<" + " OR ".join(["%r" % a for a in self.args]) + ">"

def handleAnd(tokens):
    return And(tokens.asList()[0][::2])

def handleOr(tokens):
    return Or(tokens.asList()[0][::2])

class Comparison(Node):
    def __init__(self, lh, op, rh):
        self.lh = lh
        self.op = op
        self.rh = rh
    def __repr__(self):
        return "<%s %s %s>" % (self.lh, self.op, self.rh)

def handleComparison(tokens):
    return Comparison(*tokens.asList()[0])

def handleMissing(tokens):
    pass

class Ammsc(Node):
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.expr)

class Count(Ammsc):
    pass

class Avg(Ammsc):
    pass

def handleAmmsc(klass):
    def handler(tokens):
        return klass(tokens.asList()[1])
    return handler


count_part = (
    COUNT + LPAR + "*" + RPAR |
    COUNT + LPAR + expr + RPAR).setParseAction(handleAmmsc(Count))

avg_part = (AVG + LPAR + expr + RPAR).setParseAction(handleAmmsc(Avg))

function_part = (
    function_name.setName("function_name") + LPAR + Optional(delimitedList(expr)) + RPAR)

expr_term = (
    CAST + LPAR + expr + AS + type_name + RPAR |
    EXISTS + LPAR + select_stmt + RPAR |
    count_part |
    avg_part |
    function_part |
    literal_value |
    bind_parameter |
    #identifier+'.'+identifier+'.'+identifier |
    #identifier+'.'+identifier |
    #identifier
    Combine(identifier+('.'+identifier)*(0, 2)).setParseAction(convertIdent)  # Combine does str() on tokens
    )

class BinaryExpr(Node):
    addparenth = False
    def __init__(self, args):
        self.args = args
    def __repr__(self):
        r = " ".join([str(a) for a in self.args])
        if self.addparenth:
            return "(%s)" % r
        else:
            return r

def handleBinaryExpr(strg, pos, tokens):
    toks = tokens.asList()[0]
    for t in toks:
        if hasattr(t, 'addparenth'):
            t.addparenth = True
    return BinaryExpr(toks)

class Between(Node):
    def __init__(self, expr, lower, upper):
        self.expr = expr
        self.lower = lower
        self.upper = upper

def handleBetween(strg, pos, tokens):
    return Between(
        tokens.asList()[0][0], tokens.asList()[0][2], tokens.asList()[0][4])

UNARY, BINARY, TERNARY = 1, 2, 3
expr << operatorPrecedence(expr_term,
    [
    (oneOf('- + ~') | NOT, UNARY, opAssoc.RIGHT, handleMissing),
    (ISNULL | NOTNULL | NOT + NULL, UNARY, opAssoc.LEFT, handleMissing),
    ('||', BINARY, opAssoc.LEFT, handleMissing),
    (oneOf('* / %'), BINARY, opAssoc.LEFT, handleBinaryExpr),
    (oneOf('+ -'), BINARY, opAssoc.LEFT, handleBinaryExpr),
    (oneOf('<< >> & |'), BINARY, opAssoc.LEFT, handleComparison),
    (oneOf('< <= > >='), BINARY, opAssoc.LEFT, handleComparison),
    (oneOf('= == != <>'), BINARY, opAssoc.LEFT, handleComparison),
    (IN , BINARY, opAssoc.LEFT, handleMissing),
    (IS | LIKE | GLOB | MATCH | REGEXP, BINARY, opAssoc.LEFT, handleMissing),
    ((BETWEEN,AND), TERNARY, opAssoc.LEFT, handleBetween),
    (IN + LPAR + Group(select_stmt | delimitedList(expr)) + RPAR, UNARY, opAssoc.LEFT, handleMissing),
    (AND, BINARY, opAssoc.LEFT, handleAnd),
    (OR, BINARY, opAssoc.LEFT, handleOr),
    ])

compound_operator = (UNION + Optional(ALL) | INTERSECT | EXCEPT)

ordering_term = Group(expr('order_key') + Optional(COLLATE + collation_name('collate')) + Optional(ASC | DESC)('direction'))

join_constraint = Group(Optional(ON + expr | USING + LPAR + Group(delimitedList(column_name)) + RPAR))

join_op = COMMA | Group(Optional(NATURAL) + Optional(INNER | CROSS | LEFT + OUTER | LEFT | OUTER) + JOIN)

join_source = Forward()
single_source = ( (Group(database_name("database") + "." + table_name("table")) | table_name("table")) +
                    Optional(Optional(AS) + table_alias("table_alias")) +
                    Optional(INDEXED + BY + index_name("name") | NOT + INDEXED)("index") |
                  (LPAR + select_stmt + RPAR + Optional(Optional(AS) + table_alias)) |
                  (LPAR + join_source + RPAR) )

join_source << (Group(single_source + OneOrMore(join_op + single_source + join_constraint)) |
                single_source)
group_by = Optional(GROUP + BY + Group(delimitedList(expr)("group_by_exprs")) +
                    Optional(HAVING + expr("having_expr")))

class Column(Node):
    def __init__(self, expr, alias=None):
        self.expr = expr
        self.alias = alias

    def __repr__(self):
        if self.alias:
            return "%s AS %s" % (self.expr, self.alias)
        return str(self.expr)

def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def handleColumn(strg, pos, tokens):
    tks = list(flatten(tokens.asList()))
    if len(tks) == 3:
        if tks[1] == 'AS':
            # expr AS alias
            return Column(tks[0], tks[2])

        if tks[1] == '.' and tks[2] == '*':
            return Column(Identifier(''.join(str(t) for t in tks)))
    return Column(tks[0])

result_column = ("*" | table_name + "." + "*" |
                 Group(expr + Optional(Optional(AS) + column_alias))).setParseAction(handleColumn)
select_core = (SELECT + Optional(DISTINCT | ALL) +
               Group(delimitedList(result_column))("columns") +
               Optional(FROM + join_source("from")) +
               Optional(WHERE + expr("where_expr")) +
               group_by("group_by"))

select_stmt << (select_core + ZeroOrMore(compound_operator + select_core) +
                Optional(ORDER + BY + Group(delimitedList(ordering_term))("order_by_terms")) +
                Optional(LIMIT + (Group(expr + OFFSET + expr) | Group(expr + COMMA + expr) | expr)("limit")))

# this is VERY incomplete
# http://www.sqlite.org/lang_createtable.html
column_def = Group(column_name + type_name)
create_stmt = (CREATE + TABLE + Optional(db_name.setName("db") + ".") +
               table_name.setName("table") +
               LPAR+Group(delimitedList(column_def))("columns")+RPAR)
# this is VERY incomplete
# http://www.sqlite.org/lang_insert.html
insert_stmt = (INSERT + INTO + Optional(db_name + ".") + table_name +
               LPAR+Group(delimitedList(column_name))("columns")+RPAR +
               VALUES +
               LPAR+Group(delimitedList(expr))("values")+RPAR)

tests = """\
    select * from xyzzy where z > 100
    select * from xyzzy where z > 100 order by zz
    select * from xyzzy
    select z.* from xyzzy
    select a, b from test_table where 1=1 and b='yes'
    select a, b from test_table where 1=1 and b in (select bb from foo)
    select z.a, b from test_table where 1=1 and b in (select bb from foo)
    select z.a, b from test_table where 1=1 and b in (select bb from foo) order by b,c desc,d
    select z.a, b from test_table left join test2_table where 1=1 and b in (select bb from foo)
    select a, db.table.b as BBB from db.table where 1=1 and BBB='yes'
    select a, db.table.b as BBB from test_table,db.table where 1=1 and BBB='yes'
    select a, db.table.b as BBB from test_table,db.table where 1=1 and BBB='yes' limit 50
    """.splitlines()
def main():
    for t in tests:
        t = t.strip()
        if not t: continue
        print t
        try:
            r = select_stmt.parseString(t)
            print r.dump()
        except ParseException, pe:
            print pe.msg
        print
