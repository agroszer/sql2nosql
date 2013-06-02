class Table(object):
    def __init__(self, name):
        self.name = name

class From(object):
    def __init__(self, tables):
        self.tables = tables

class Select(object):
    def __init__(self, all_distinct, fields, args):
        self.all_distinct = all_distinct
        self.fields = fields
        self.args = args


tokens =  ['NAME', 'STRING', 'INTNUM', 'APPROXNUM', 'OR', 'AND', 'NOT',
           'COMPARISON', 'UMINUS', 'ALL', 'AMMSC', 'ANY', 'AS', 'ASC',
           'AUTHORIZATION', 'BETWEEN', 'BY', 'CHARACTER', 'CHECK', 'CLOSE',
           'COMMIT', 'CONTINUE', 'CREATE', 'CURRENT', 'CURSOR', 'DECIMAL',
           'DECLARE', 'DEFAULT', 'DELETE', 'DESC', 'DISTINCT', 'DOUBLE',
           'ESCAPE', 'EXISTS', 'FETCH', 'FLOAT', 'FOR', 'FOREIGN', 'FOUND',
           'FROM', 'GOTO', 'GRANT', 'GROUP', 'HAVING', 'IN', 'INDICATOR',
           'INSERT', 'INTEGER', 'INTO', 'IS', 'KEY', 'LANGUAGE', 'LIKE',
           'MODULE', 'NULLX', 'NUMERIC', 'OF', 'ON', 'OPEN', 'OPTION',
           'ORDER', 'PRECISION', 'PRIMARY', 'PRIVILEGES', 'PROCEDURE',
           'PUBLIC', 'REAL', 'REFERENCES', 'ROLLBACK', 'SCHEMA', 'SELECT',
           'SET', 'SMALLINT', 'SOME', 'SQLCODE', 'SQLERROR', 'TABLE', 'TO',
           'UNION', 'UNIQUE', 'UPDATE', 'USER', 'VALUES', 'VIEW', 'WHENEVER',
           'WHERE', 'WITH', 'WORK', 'COBOL', 'FORTRAN', 'PASCAL', 'PLI', 'C',
           'ADA']

precedence =  [('left', 'OR'),
    ('left', 'AND'),
    ('left', 'NOT'),
    ('left', 'COMPARISON'),
    ('left', "+", "-"),
    ('left', "*", "/"),
    ('nonassoc', 'UMINUS')]


class Lexer(object):
    tokens = tokens
    t_ignore = ' \t\n\r'

    def t_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    # function ordering matters!
    def t_ADA(self,t):
        r"ADA"
        return t
    def t_ALL(self,t):
        r"ALL"
        return t
    def t_AND(self,t):
        r"AND"
        return t
    def t_AMMSC(self,t):
        r"AVG|MIN|MAX|SUM|COUNT"
        return t
    def t_ANY(self,t):
        r"ANY"
        return t
    def t_AS(self,t):
        r"AS"
        return t
    def t_ASC(self,t):
        r"ASC"
        return t
    def t_AUTHORIZATION(self,t):
        r"AUTHORIZATION"
        return t
    def t_BETWEEN(self,t):
        r"BETWEEN"
        return t
    def t_BY(self,t):
        r"BY"
        return t
    def t_C(self,t):
        r"C"
        return t
    def t_CHARACTER(self,t):
        r"CHAR(ACTER)?"
        return t
    def t_CHECK(self,t):
        r"CHECK"
        return t
    def t_CLOSE(self,t):
        r"CLOSE"
        return t
    def t_COBOL(self,t):
        r"COBOL"
        return t
    def t_COMMIT(self,t):
        r"COMMIT"
        return t
    def t_CONTINUE(self,t):
        r"CONTINUE"
        return t
    def t_CREATE(self,t):
        r"CREATE"
        return t
    def t_CURRENT(self,t):
        r"CURRENT"
        return t
    def t_CURSOR(self,t):
        r"CURSOR"
        return t
    def t_DECIMAL(self,t):
        r"DECIMAL"
        return t
    def t_DECLARE(self,t):
        r"DECLARE"
        return t
    def t_DEFAULT(self,t):
        r"DEFAULT"
        return t
    def t_DELETE(self,t):
        r"DELETE"
        return t
    def t_DESC(self,t):
        r"DESC"
        return t
    def t_DISTINCT(self,t):
        r"DISTINC"
        return t
    def t_DOUBLE(self,t):
        r"DOUBLE"
        return t
    def t_ESCAPE(self,t):
        r"ESCAPE"
        return t
    def t_EXISTS(self,t):
        r"EXISTS"
        return t
    def t_FETCH(self,t):
        r"FETCH"
        return t
    def t_FLOAT(self,t):
        r"FLOAT"
        return t
    def t_FOR(self,t):
        r"FOR"
        return t
    def t_FOREIGN(self,t):
        r"FOREIGN"
        return t
    def t_FORTRAN(self,t):
        r"FORTRAN"
        return t
    def t_FOUND(self,t):
        r"FOUND"
        return t
    def t_FROM(self,t):
        r"FROM"
        return t
    def t_GOTO(self, t):
        r"GO[ \t]*TO"
        return t
    def t_GRANT(self,t):
        r"GRANT"
        return t
    def t_GROUP(self,t):
        r"GROUP"
        return t
    def t_HAVING(self,t):
        r"HAVING"
        return t
    def t_IN(self,t):
        r"IN"
        return t
    def t_INDICATOR(self,t):
        r"INDICATOR"
        return t
    def t_INSERT(self,t):
        r"INSERT"
        return t
    def t_INTEGER(self,t):
        r"INT(EGER)?"
        return t
    def t_INTO(self,t):
        r"INTO"
        return t
    def t_IS(self,t):
        r"IS"
        return t
    def t_KEY(self,t):
        r"KEY"
        return t
    def t_LANGUAGE(self,t):
        r"LANGUAG"
        return t
    def t_LIKE(self,t):
        r"LIKE"
        return t
    def t_MODULE(self,t):
        r"MODULE"
        return t
    def t_NOT(self,t):
        r"NOT"
        return t
    def t_NULLX(self,t):
        r"NULL"
        return t
    def t_NUMERIC(self,t):
        r"NUMERIC"
        return t
    def t_OF(self,t):
        r"OF"
        return t
    def t_ON(self,t):
        r"ON"
        return t
    def t_OPEN(self,t):
        r"OPEN"
        return t
    def t_OPTION(self,t):
        r"OPTION"
        return t
    def t_OR(self,t):
        r"OR"
        return t
    def t_ORDER(self,t):
        r"ORDER"
        return t
    def t_PASCAL(self,t):
        r"PASCAL"
        return t
    def t_PLI(self,t):
        r"PLI"
        return t
    def t_PRECISION(self,t):
        r"PRECISION"
        return t
    def t_PRIMARY(self,t):
        r"PRIMARY"
        return t
    def t_PRIVILEGES(self,t):
        r"PRIVILEGES"
        return t
    def t_PROCEDURE(self,t):
        r"PROCEDURE"
        return t
    def t_PUBLIC(self,t):
        r"PUBLIC"
        return t
    def t_REAL(self,t):
        r"REAL"
        return t
    def t_REFERENCES(self,t):
        r"REFERENCES"
        return t
    def t_ROLLBACK(self,t):
        r"ROLLBACK"
        return t
    def t_SCHEMA(self,t):
        r"SCHEMA"
        return t
    #t_SELECT = "SELECT"
    def t_SELECT(self,t):
        r"SELECT"
        return t
    def t_SET(self,t):
        r"SET"
        return t
    def t_SMALLINT(self,t):
        r"SMALLINT"
        return t
    def t_SOME(self,t):
        r"SOME"
        return t
    def t_SQLCODE(self,t):
        r"SQLCODE"
        return t
    def t_TABLE(self,t):
        r"TABLE"
        return t
    def t_TO(self,t):
        r"TO"
        return t
    def t_UNION(self,t):
        r"UNION"
        return t
    def t_UNIQUE(self,t):
        r"UNIQUE"
        return t
    def t_UPDATE(self,t):
        r"UPDATE"
        return t
    def t_USER(self,t):
        r"USER"
        return t
    def t_VALUES(self,t):
        r"VALUES"
        return t
    def t_VIEW(self,t):
        r"VIEW"
        return t
    def t_WHENEVER(self,t):
        r"WHENEVER"
        return t
    def t_WHERE(self,t):
        r"WHERE"
        return t
    def t_WITH(self,t):
        r"WITH"
        return t
    def t_WORK(self,t):
        r"WORK"
        return t

    def t_COMPARISON(self,t):
        r"=|<>|<|>|<=|>="
        return t

    literals = "[-+*/:(),.;]"

    def t_NAME(self,t):
        r"[A-Za-z][A-Za-z0-9_]*"
        return t

#/* numbers */
    def t_INTNUM(self,t):
        r"([0-9]+)|([0-9]+[.][0-9]*)|([.][0-9]*)"
        return t

    def t_APPROXNUM(self,t):
        r"([0-9]+[eE][+-]?[0-9]+)|[0-9]+[.][0-9]*[eE][+-]?[0-9]+|[.][0-9]*[eE][+-]?[0-9]+"
        return t

    def t_STRING(self, t):
        r''''(\\.|[^\'])*\'|"(\\.|[^"])*"'''
        return t


# -------------- RULES ----------------

def p_sql_list_1(p):
    r"""sql_list : sql ';'"""
    p[0] = (p[1],)


def p_sql_list_2(p):
    r"""sql_list : sql_list sql ';'"""
    p[0] = p[1]+p[2]


def p_sql_1(p):
    r"""sql : schema"""
    #from dbgp.client import brk; brk('127.0.0.1')


def p_schema_1(p):
    r"""schema : CREATE SCHEMA AUTHORIZATION user opt_schema_element_list"""

def p_opt_schema_element_list_1(p):
    r"""opt_schema_element_list : """

def p_opt_schema_element_list_2(p):
    r"""opt_schema_element_list : schema_element_list"""

def p_schema_element_list_1(p):
    r"""schema_element_list : schema_element"""

def p_schema_element_list_2(p):
    r"""schema_element_list : schema_element_list schema_element"""

def p_schema_element_1(p):
    r"""schema_element : base_table_def"""

def p_schema_element_2(p):
    r"""schema_element : view_def"""

def p_schema_element_3(p):
    r"""schema_element : privilege_def"""

def p_base_table_def_1(p):
    r"""base_table_def : CREATE TABLE table '(' base_table_element_commalist ')'"""

def p_base_table_element_commalist_1(p):
    r"""base_table_element_commalist : base_table_element"""

def p_base_table_element_commalist_2(p):
    r"""base_table_element_commalist : base_table_element_commalist ',' base_table_element"""

def p_base_table_element_1(p):
    r"""base_table_element : column_def"""

def p_base_table_element_2(p):
    r"""base_table_element : table_constraint_def"""

def p_column_def_1(p):
    r"""column_def : column data_type column_def_opt_list"""

def p_column_def_opt_list_1(p):
    r"""column_def_opt_list : """

def p_column_def_opt_list_2(p):
    r"""column_def_opt_list : column_def_opt_list column_def_opt"""

def p_column_def_opt_1(p):
    r"""column_def_opt : NOT NULLX"""

def p_column_def_opt_2(p):
    r"""column_def_opt : NOT NULLX UNIQUE"""

def p_column_def_opt_3(p):
    r"""column_def_opt : NOT NULLX PRIMARY KEY"""

def p_column_def_opt_4(p):
    r"""column_def_opt : DEFAULT literal"""

def p_column_def_opt_5(p):
    r"""column_def_opt : DEFAULT NULLX"""

def p_column_def_opt_6(p):
    r"""column_def_opt : DEFAULT USER"""

def p_column_def_opt_7(p):
    r"""column_def_opt : CHECK '(' search_condition ')'"""

def p_column_def_opt_8(p):
    r"""column_def_opt : REFERENCES table"""

def p_column_def_opt_9(p):
    r"""column_def_opt : REFERENCES table '(' column_commalist ')'"""

def p_table_constraint_def_1(p):
    r"""table_constraint_def : UNIQUE '(' column_commalist ')'"""

def p_table_constraint_def_2(p):
    r"""table_constraint_def : PRIMARY KEY '(' column_commalist ')'"""

def p_table_constraint_def_3(p):
    r"""table_constraint_def : FOREIGN KEY '(' column_commalist ')' REFERENCES table"""

def p_table_constraint_def_4(p):
    r"""table_constraint_def : FOREIGN KEY '(' column_commalist ')' REFERENCES table '(' column_commalist ')'"""

def p_table_constraint_def_5(p):
    r"""table_constraint_def : CHECK '(' search_condition ')'"""

def p_column_commalist_1(p):
    r"""column_commalist : column"""

def p_column_commalist_2(p):
    r"""column_commalist : column_commalist ',' column"""

def p_view_def_1(p):
    r"""view_def : CREATE VIEW table opt_column_commalist AS query_spec opt_with_check_option"""

def p_opt_with_check_option_1(p):
    r"""opt_with_check_option : """

def p_opt_with_check_option_2(p):
    r"""opt_with_check_option : WITH CHECK OPTION"""

def p_opt_column_commalist_1(p):
    r"""opt_column_commalist : """

def p_opt_column_commalist_2(p):
    r"""opt_column_commalist : '(' column_commalist ')'"""

def p_privilege_def_1(p):
    r"""privilege_def : GRANT privileges ON table TO grantee_commalist opt_with_grant_option"""

def p_opt_with_grant_option_1(p):
    r"""opt_with_grant_option : """

def p_opt_with_grant_option_2(p):
    r"""opt_with_grant_option : WITH GRANT OPTION"""

def p_privileges_1(p):
    r"""privileges : ALL PRIVILEGES"""

def p_privileges_2(p):
    r"""privileges : ALL"""

def p_privileges_3(p):
    r"""privileges : operation_commalist"""

def p_operation_commalist_1(p):
    r"""operation_commalist : operation"""

def p_operation_commalist_2(p):
    r"""operation_commalist : operation_commalist ',' operation"""

def p_operation_1(p):
    r"""operation : SELECT"""
    #from dbgp.client import brk; brk('127.0.0.1')


def p_operation_2(p):
    r"""operation : INSERT"""

def p_operation_3(p):
    r"""operation : DELETE"""

def p_operation_4(p):
    r"""operation : UPDATE opt_column_commalist"""

def p_operation_5(p):
    r"""operation : REFERENCES opt_column_commalist"""

def p_grantee_commalist_1(p):
    r"""grantee_commalist : grantee"""

def p_grantee_commalist_2(p):
    r"""grantee_commalist : grantee_commalist ',' grantee"""

def p_grantee_1(p):
    r"""grantee : PUBLIC"""

def p_grantee_2(p):
    r"""grantee : user"""

def p_sql_2(p):
    r"""sql : module_def"""

def p_module_def_1(p):
    r"""module_def : MODULE opt_module LANGUAGE lang AUTHORIZATION user opt_cursor_def_list procedure_def_list"""

def p_opt_module_1(p):
    r"""opt_module : """

def p_opt_module_2(p):
    r"""opt_module : module"""

def p_lang_1(p):
    r"""lang : COBOL"""

def p_lang_2(p):
    r"""lang : FORTRAN"""

def p_lang_3(p):
    r"""lang : PASCAL"""

def p_lang_4(p):
    r"""lang : PLI"""

def p_lang_5(p):
    r"""lang : C"""

def p_lang_6(p):
    r"""lang : ADA"""

def p_opt_cursor_def_list_1(p):
    r"""opt_cursor_def_list : """

def p_opt_cursor_def_list_2(p):
    r"""opt_cursor_def_list : cursor_def_list"""

def p_cursor_def_list_1(p):
    r"""cursor_def_list : cursor_def"""

def p_cursor_def_list_2(p):
    r"""cursor_def_list : cursor_def_list cursor_def"""

def p_cursor_def_1(p):
    r"""cursor_def : DECLARE cursor CURSOR FOR query_exp opt_order_by_clause"""

def p_opt_order_by_clause_1(p):
    r"""opt_order_by_clause : """

def p_opt_order_by_clause_2(p):
    r"""opt_order_by_clause : ORDER BY ordering_spec_commalist"""

def p_ordering_spec_commalist_1(p):
    r"""ordering_spec_commalist : ordering_spec"""

def p_ordering_spec_commalist_2(p):
    r"""ordering_spec_commalist : ordering_spec_commalist ',' ordering_spec"""

def p_ordering_spec_1(p):
    r"""ordering_spec : INTNUM opt_asc_desc"""

def p_ordering_spec_2(p):
    r"""ordering_spec : column_ref opt_asc_desc"""

def p_opt_asc_desc_1(p):
    r"""opt_asc_desc : """

def p_opt_asc_desc_2(p):
    r"""opt_asc_desc : ASC"""

def p_opt_asc_desc_3(p):
    r"""opt_asc_desc : DESC"""

def p_procedure_def_list_1(p):
    r"""procedure_def_list : procedure_def"""

def p_procedure_def_list_2(p):
    r"""procedure_def_list : procedure_def_list procedure_def"""

def p_procedure_def_1(p):
    r"""procedure_def : PROCEDURE procedure parameter_def_list ';' manipulative_statement_list"""

def p_manipulative_statement_list_1(p):
    r"""manipulative_statement_list : manipulative_statement"""
    p[0] = (p[1], )

def p_manipulative_statement_list_2(p):
    r"""manipulative_statement_list : manipulative_statement_list manipulative_statement"""
    p[0] = p[1]+p[2]

def p_parameter_def_list_1(p):
    r"""parameter_def_list : parameter_def"""

def p_parameter_def_list_2(p):
    r"""parameter_def_list : parameter_def_list parameter_def"""

def p_parameter_def_1(p):
    r"""parameter_def : parameter data_type"""

def p_parameter_def_2(p):
    r"""parameter_def : SQLCODE"""

def p_sql_3(p):
    r"""sql : manipulative_statement"""
    p[0] = p[1]

def p_manipulative_statement_1(p):
    r"""manipulative_statement : close_statement"""

def p_manipulative_statement_2(p):
    r"""manipulative_statement : commit_statement"""

def p_manipulative_statement_3(p):
    r"""manipulative_statement : delete_statement_positioned"""

def p_manipulative_statement_4(p):
    r"""manipulative_statement : delete_statement_searched"""

def p_manipulative_statement_5(p):
    r"""manipulative_statement : fetch_statement"""

def p_manipulative_statement_6(p):
    r"""manipulative_statement : insert_statement"""

def p_manipulative_statement_7(p):
    r"""manipulative_statement : open_statement"""

def p_manipulative_statement_8(p):
    r"""manipulative_statement : rollback_statement"""

def p_manipulative_statement_9(p):
    r"""manipulative_statement : select_statement"""
    p[0] = p[1]

def p_manipulative_statement_10(p):
    r"""manipulative_statement : update_statement_positioned"""

def p_manipulative_statement_11(p):
    r"""manipulative_statement : update_statement_searched"""

def p_close_statement_1(p):
    r"""close_statement : CLOSE cursor"""

def p_commit_statement_1(p):
    r"""commit_statement : COMMIT WORK"""

def p_delete_statement_positioned_1(p):
    r"""delete_statement_positioned : DELETE FROM table WHERE CURRENT OF cursor"""

def p_delete_statement_searched_1(p):
    r"""delete_statement_searched : DELETE FROM table opt_where_clause"""

def p_fetch_statement_1(p):
    r"""fetch_statement : FETCH cursor INTO target_commalist"""

def p_insert_statement_1(p):
    r"""insert_statement : INSERT INTO table opt_column_commalist values_or_query_spec"""

def p_values_or_query_spec_1(p):
    r"""values_or_query_spec : VALUES '(' insert_atom_commalist ')'"""

def p_values_or_query_spec_2(p):
    r"""values_or_query_spec : query_spec"""

def p_insert_atom_commalist_1(p):
    r"""insert_atom_commalist : insert_atom"""

def p_insert_atom_commalist_2(p):
    r"""insert_atom_commalist : insert_atom_commalist ',' insert_atom"""

def p_insert_atom_1(p):
    r"""insert_atom : atom"""

def p_insert_atom_2(p):
    r"""insert_atom : NULLX"""

def p_open_statement_1(p):
    r"""open_statement : OPEN cursor"""

def p_rollback_statement_1(p):
    r"""rollback_statement : ROLLBACK WORK"""

def p_select_statement_1(p):
    r"""select_statement : SELECT opt_all_distinct selection table_exp"""
    #from dbgp.client import brk; brk('127.0.0.1')
    p[0] = Select(all_distinct=p[2], fields=p[3], args=p[4])

def p_select_statement_2(p):
    r"""select_statement : SELECT opt_all_distinct selection table_exp INTO target_commalist"""
    #from dbgp.client import brk; brk('127.0.0.1')


def p_opt_all_distinct_1(p):
    r"""opt_all_distinct : """
    #from dbgp.client import brk; brk('127.0.0.1')


def p_opt_all_distinct_2(p):
    r"""opt_all_distinct : ALL"""

def p_opt_all_distinct_3(p):
    r"""opt_all_distinct : DISTINCT"""

def p_update_statement_positioned_1(p):
    r"""update_statement_positioned : UPDATE table SET assignment_commalist WHERE CURRENT OF cursor"""

def p_assignment_commalist_1(p):
    r"""assignment_commalist : """

def p_assignment_commalist_2(p):
    r"""assignment_commalist : assignment"""

def p_assignment_commalist_3(p):
    r"""assignment_commalist : assignment_commalist ',' assignment"""

def p_assignment_1(p):
    r"""assignment : column '=' scalar_exp"""

def p_assignment_2(p):
    r"""assignment : column '=' NULLX"""

def p_update_statement_searched_1(p):
    r"""update_statement_searched : UPDATE table SET assignment_commalist opt_where_clause"""

def p_target_commalist_1(p):
    r"""target_commalist : target"""

def p_target_commalist_2(p):
    r"""target_commalist : target_commalist ',' target"""

def p_target_1(p):
    r"""target : parameter_ref"""

def p_opt_where_clause_1(p):
    r"""opt_where_clause : """

def p_opt_where_clause_2(p):
    r"""opt_where_clause : where_clause"""

def p_query_exp_1(p):
    r"""query_exp : query_term"""

def p_query_exp_2(p):
    r"""query_exp : query_exp UNION query_term"""

def p_query_exp_3(p):
    r"""query_exp : query_exp UNION ALL query_term"""

def p_query_term_1(p):
    r"""query_term : query_spec"""

def p_query_term_2(p):
    r"""query_term : '(' query_exp ')'"""

def p_query_spec_1(p):
    r"""query_spec : SELECT opt_all_distinct selection table_exp"""
    #from dbgp.client import brk; brk('127.0.0.1')


def p_selection_1(p):
    r"""selection : scalar_exp_commalist"""

def p_selection_2(p):
    r"""selection : '*'"""
    p[0] = p[1]


def p_table_exp_1(p):
    r"""table_exp : from_clause opt_where_clause opt_group_by_clause opt_having_clause"""
    #from dbgp.client import brk; brk('127.0.0.1')
    o = (p[1], p[2], p[3], p[4])
    p[0] = tuple(i for i in o if i is not None)


def p_from_clause_1(p):
    r"""from_clause : FROM table_ref_commalist"""
    #from dbgp.client import brk; brk('127.0.0.1')
    p[0] = From(p[2])


def p_table_ref_commalist_1(p):
    r"""table_ref_commalist : table_ref"""
    #from dbgp.client import brk; brk('127.0.0.1')
    p[0] = (p[1], )


def p_table_ref_commalist_2(p):
    r"""table_ref_commalist : table_ref_commalist ',' table_ref"""
    #from dbgp.client import brk; brk('127.0.0.1')
    p[0] = p[1] + p[2]


def p_table_ref_1(p):
    r"""table_ref : table"""
    #from dbgp.client import brk; brk('127.0.0.1')
    p[0] = p[1]


def p_table_ref_2(p):
    r"""table_ref : table range_variable"""
    #from dbgp.client import brk; brk('127.0.0.1')


def p_where_clause_1(p):
    r"""where_clause : WHERE search_condition"""

def p_opt_group_by_clause_1(p):
    r"""opt_group_by_clause : """

def p_opt_group_by_clause_2(p):
    r"""opt_group_by_clause : GROUP BY column_ref_commalist"""

def p_column_ref_commalist_1(p):
    r"""column_ref_commalist : column_ref"""

def p_column_ref_commalist_2(p):
    r"""column_ref_commalist : column_ref_commalist ',' column_ref"""

def p_opt_having_clause_1(p):
    r"""opt_having_clause : """

def p_opt_having_clause_2(p):
    r"""opt_having_clause : HAVING search_condition"""

def p_search_condition_1(p):
    r"""search_condition : """

def p_search_condition_2(p):
    r"""search_condition : search_condition OR search_condition"""

def p_search_condition_3(p):
    r"""search_condition : search_condition AND search_condition"""

def p_search_condition_4(p):
    r"""search_condition : NOT search_condition"""

def p_search_condition_5(p):
    r"""search_condition : '(' search_condition ')'"""

def p_search_condition_6(p):
    r"""search_condition : predicate"""

def p_predicate_1(p):
    r"""predicate : comparison_predicate"""

def p_predicate_2(p):
    r"""predicate : between_predicate"""

def p_predicate_3(p):
    r"""predicate : like_predicate"""

def p_predicate_4(p):
    r"""predicate : test_for_null"""

def p_predicate_5(p):
    r"""predicate : in_predicate"""

def p_predicate_6(p):
    r"""predicate : all_or_any_predicate"""

def p_predicate_7(p):
    r"""predicate : existence_test"""

def p_comparison_predicate_1(p):
    r"""comparison_predicate : scalar_exp COMPARISON scalar_exp"""

def p_comparison_predicate_2(p):
    r"""comparison_predicate : scalar_exp COMPARISON subquery"""

def p_between_predicate_1(p):
    r"""between_predicate : scalar_exp NOT BETWEEN scalar_exp AND scalar_exp"""

def p_between_predicate_2(p):
    r"""between_predicate : scalar_exp BETWEEN scalar_exp AND scalar_exp"""

def p_like_predicate_1(p):
    r"""like_predicate : scalar_exp NOT LIKE atom opt_escape"""

def p_like_predicate_2(p):
    r"""like_predicate : scalar_exp LIKE atom opt_escape"""

def p_opt_escape_1(p):
    r"""opt_escape : """

def p_opt_escape_2(p):
    r"""opt_escape : ESCAPE atom"""

def p_test_for_null_1(p):
    r"""test_for_null : column_ref IS NOT NULLX"""

def p_test_for_null_2(p):
    r"""test_for_null : column_ref IS NULLX"""

def p_in_predicate_1(p):
    r"""in_predicate : scalar_exp NOT IN '(' subquery ')'"""

def p_in_predicate_2(p):
    r"""in_predicate : scalar_exp IN '(' subquery ')'"""

def p_in_predicate_3(p):
    r"""in_predicate : scalar_exp NOT IN '(' atom_commalist ')'"""

def p_in_predicate_4(p):
    r"""in_predicate : scalar_exp IN '(' atom_commalist ')'"""

def p_atom_commalist_1(p):
    r"""atom_commalist : atom"""

def p_atom_commalist_2(p):
    r"""atom_commalist : atom_commalist ',' atom"""

def p_all_or_any_predicate_1(p):
    r"""all_or_any_predicate : scalar_exp COMPARISON any_all_some subquery"""

def p_any_all_some_1(p):
    r"""any_all_some : ANY"""

def p_any_all_some_2(p):
    r"""any_all_some : ALL"""

def p_any_all_some_3(p):
    r"""any_all_some : SOME"""

def p_existence_test_1(p):
    r"""existence_test : EXISTS subquery"""

def p_subquery_1(p):
    r"""subquery : '(' SELECT opt_all_distinct selection table_exp ')'"""

def p_scalar_exp_1(p):
    r"""scalar_exp : scalar_exp '+' scalar_exp"""

def p_scalar_exp_2(p):
    r"""scalar_exp : scalar_exp '-' scalar_exp"""

def p_scalar_exp_3(p):
    r"""scalar_exp : scalar_exp '*' scalar_exp"""

def p_scalar_exp_4(p):
    r"""scalar_exp : scalar_exp '/' scalar_exp"""

def p_scalar_exp_5(p):
    r"""scalar_exp : '+' scalar_exp %prec UMINUS"""

def p_scalar_exp_6(p):
    r"""scalar_exp : '-' scalar_exp %prec UMINUS"""

def p_scalar_exp_7(p):
    r"""scalar_exp : atom"""

def p_scalar_exp_8(p):
    r"""scalar_exp : column_ref"""

def p_scalar_exp_9(p):
    r"""scalar_exp : function_ref"""

def p_scalar_exp_10(p):
    r"""scalar_exp : '(' scalar_exp ')'"""

def p_scalar_exp_commalist_1(p):
    r"""scalar_exp_commalist : scalar_exp"""

def p_scalar_exp_commalist_2(p):
    r"""scalar_exp_commalist : scalar_exp_commalist ',' scalar_exp"""

def p_atom_1(p):
    r"""atom : parameter_ref"""

def p_atom_2(p):
    r"""atom : literal"""

def p_atom_3(p):
    r"""atom : USER"""

def p_parameter_ref_1(p):
    r"""parameter_ref : parameter"""

def p_parameter_ref_2(p):
    r"""parameter_ref : parameter parameter"""

def p_parameter_ref_3(p):
    r"""parameter_ref : parameter INDICATOR parameter"""

def p_function_ref_1(p):
    r"""function_ref : AMMSC '(' '*' ')'"""

def p_function_ref_2(p):
    r"""function_ref : AMMSC '(' DISTINCT column_ref ')'"""

def p_function_ref_3(p):
    r"""function_ref : AMMSC '(' ALL scalar_exp ')'"""

def p_function_ref_4(p):
    r"""function_ref : AMMSC '(' scalar_exp ')'"""

def p_literal_1(p):
    r"""literal : STRING"""

def p_literal_2(p):
    r"""literal : INTNUM"""

def p_literal_3(p):
    r"""literal : APPROXNUM"""

def p_table_1(p):
    r"""table : NAME"""
    #from dbgp.client import brk; brk('127.0.0.1')
    p[0] = Table(p[1])


def p_table_2(p):
    r"""table : NAME '.' NAME"""

def p_column_ref_1(p):
    r"""column_ref : NAME"""

def p_column_ref_2(p):
    r"""column_ref : NAME '.' NAME"""

def p_column_ref_3(p):
    r"""column_ref : NAME '.' NAME '.' NAME"""

def p_data_type_1(p):
    r"""data_type : CHARACTER"""

def p_data_type_2(p):
    r"""data_type : CHARACTER '(' INTNUM ')'"""

def p_data_type_3(p):
    r"""data_type : NUMERIC"""

def p_data_type_4(p):
    r"""data_type : NUMERIC '(' INTNUM ')'"""

def p_data_type_5(p):
    r"""data_type : NUMERIC '(' INTNUM ',' INTNUM ')'"""

def p_data_type_6(p):
    r"""data_type : DECIMAL"""

def p_data_type_7(p):
    r"""data_type : DECIMAL '(' INTNUM ')'"""

def p_data_type_8(p):
    r"""data_type : DECIMAL '(' INTNUM ',' INTNUM ')'"""

def p_data_type_9(p):
    r"""data_type : INTEGER"""

def p_data_type_10(p):
    r"""data_type : SMALLINT"""

def p_data_type_11(p):
    r"""data_type : FLOAT"""

def p_data_type_12(p):
    r"""data_type : FLOAT '(' INTNUM ')'"""

def p_data_type_13(p):
    r"""data_type : REAL"""

def p_data_type_14(p):
    r"""data_type : DOUBLE PRECISION"""

def p_column_1(p):
    r"""column : NAME"""

def p_cursor_1(p):
    r"""cursor : NAME"""

def p_module_1(p):
    r"""module : NAME"""

def p_parameter_1(p):
    r"""parameter : ':' NAME"""

def p_procedure_1(p):
    r"""procedure : NAME"""

def p_range_variable_1(p):
    r"""range_variable : NAME"""

def p_user_1(p):
    r"""user : NAME"""

def p_sql_4(p):
    r"""sql : WHENEVER NOT FOUND when_action"""

def p_sql_5(p):
    r"""sql : WHENEVER SQLERROR when_action"""

def p_when_action_1(p):
    r"""when_action : GOTO NAME"""

def p_when_action_2(p):
    r"""when_action : CONTINUE"""

def p_error(t):
    #from dbgp.client import brk; brk('127.0.0.1')

    print "Syntax error at '%s' (%s)" % (t.value, t.lexpos)

# -------------- RULES END ----------------
#

from ply import lex, yacc

LEXER = lex.lex(object=Lexer(), debug=False)
#PARSERS = local()

def parse(str):
    lexer = LEXER.clone()

    #lexer.input(str)
    ##from dbgp.client import brk; brk('127.0.0.1')
    #
    #for tok in iter(lexer.token, None):
    #    print repr(tok.type), repr(tok.value)

    #global PARSERS
    #try:
    #    parser = PARSERS.parser
    #
    #    try:
    #        parser.restart()
    #    except AttributeError:
    #        pass
    #
    #except AttributeError:
    #    parser = yacc.yacc(module = Parser(metadata))
    #    PARSERS.parser = parser

    try:
        parser = yacc.yacc(debug=True)

        #from dbgp.client import brk; brk('127.0.0.1')

        retval = parser.parse(str, lexer=lexer, debug=0)
    except Exception, e:
        print e
        raise
    return retval

if __name__ == '__main__':
    yacc.yacc()
