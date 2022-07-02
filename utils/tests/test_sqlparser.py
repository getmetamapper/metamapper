"""
import utils.sqlparser as sqlparser

with open('./utils/tests/sqlparser/account_dimensions.sql') as f:
    sql = f.read()

parser = sqlparser.Parser(sql, session_db="MAIN_STAGE", session_schema="public")
parser.get_tables()
"""
