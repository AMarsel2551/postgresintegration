import psycopg2
from postgresintegration.settings import db_settings


class DatabaseConnector:
    def __init__(self, schema_name: str):
        self.dbname = db_settings.NAME
        self.schema_name = schema_name
        self.user = db_settings.USER_NAME
        self.password = db_settings.USER_PASSWORD
        self.host = db_settings.IP_ADDRESS
        self.port = db_settings.IP_PORT
        self.connection = None

        self.functions = None
        self.connect()

    def connect(self):
        self.connection = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    def get_postgres_functions(self):
        query = f"""
        SELECT
            proname AS function_name,
            pg_catalog.pg_get_functiondef(p.oid) AS definition,
            pg_catalog.pg_get_function_identity_arguments(p.oid) AS arguments,
            pg_catalog.pg_get_function_result(p.oid) AS result
        FROM
            pg_catalog.pg_proc p
        LEFT JOIN
            pg_catalog.pg_namespace n ON n.oid = p.pronamespace
        WHERE
            n.nspname = '{self.schema_name}'
            AND p.prokind = 'f';
        """
        cur = self.connection.cursor()
        cur.execute(query)
        self.functions = cur.fetchall()
        cur.close()
        self.disconnect()
        return self.functions

    def get_postgres_table(self):
        query = f"""
        SELECT
            c.relname as table_name,
            a.attname AS column_name,
            pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type
        FROM
            pg_catalog.pg_class c
        JOIN
            pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        JOIN
            pg_catalog.pg_attribute a ON a.attrelid = c.oid
        WHERE
            n.nspname = '{self.schema_name}'
            AND c.relkind = 'r'
            AND a.attnum > 0
            AND NOT a.attisdropped
        ORDER BY a.attnum;
        """
        cur = self.connection.cursor()
        cur.execute(query)
        self.functions = cur.fetchall()
        cur.close()
        self.disconnect()
        return self.functions

    def disconnect(self) -> None:
        if self.connection:
            self.connection.close()

