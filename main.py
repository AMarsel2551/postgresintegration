import psycopg2, os, copy
from logger import log
from settings import db_settings


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
        print(self.connection)
        cur = self.connection.cursor()
        cur.execute(query)
        self.functions = cur.fetchall()
        cur.close()
        self.disconnect()
        return self.functions

    def disconnect(self) -> None:
        if self.connection:
            self.connection.close()


class PostgresFunctionGenerator:
    def __init__(
            self,
            schema_name: str,
            file_name: str = None, path: str = None, imports: list = None,
            asynchronous: bool = False, decorators: list = None, arguments: str = None, prefix: str = None
    ):
        self.connector = DatabaseConnector(schema_name=schema_name)
        self.functions = self.connector.get_postgres_functions()

        self.schema_name = schema_name
        self.python_functions = []
        self.path = path
        self.file_name = file_name + '.py' or 'generated_functions.py'
        self.imports = list(set((imports or []) + ['from typing import Any\nfrom datetime import datetime']))
        self.arguments = list(set((arguments or []) + ['connection']))
        self.prefix = prefix
        self.decorators = decorators or []
        self.asynchronous = asynchronous

    def generate_function_name(self, function_name: str, suffix: str):
        if self.prefix is not None:
            function_name = f"{self.prefix}_{function_name}{suffix}"
        else:
            function_name = f"{function_name}{suffix}"

        return function_name

    def generate_funcrion_arguments(self, sql_arguments) -> [str, str, str]:
        type_mapping = {
            "bigint": "int",
            "character": "str",
            "character varying": "str",
            "text": "str",
            "boolean": "bool",
            "integer": "int",
            "numeric": "float",
            "real": "float",
            "double": "float",
            "jsonb": "str",  # todo поменять!
            "json": "str",  # todo поменять!
            "bigint[]": "list[int]",
            "timestamp": "datetime",
            "date": "datetime"
        }
        args_list = sql_arguments.split(', ')
        sql_args = [f"${i + 1}" for i in range(len(args_list))]
        python_args = copy.deepcopy(self.arguments)
        funcion_args = []

        for arg in args_list:
            if arg == '':
                break
            a = arg.split(' ')
            arg_name = a[0]
            arg_type = type_mapping.get(a[1])

            # Исключение из-за OUT
            if arg_name == 'OUT':
                arg_name = a[1]
                arg_type = type_mapping.get(a[2])

            # Убираем " из аргументов функции
            arg_name = arg_name.strip('"')

            funcion_args.append(arg_name)
            if not arg_type:
                log.error(f"arg_type is {arg_type} sql_arg: {a[0]} sql_arg_type: {a[1]}")
                python_args.append(f"{arg_name}: Any=None")
            else:
                python_args.append(f"{arg_name}: {arg_type}=None")

        return ', '.join(python_args), ', '.join(funcion_args), ', '.join(sql_args)

    def generate_python_function(self, function_name: str, sql_arguments: str, result: str, suffix: str = "") -> str:
        # Аргументы для python функции (a, b, c) и ($1, $2, $3)
        python_args, funcion_args, sql_args = self.generate_funcrion_arguments(sql_arguments=sql_arguments)

        # Генерация названия функции
        function_name = self.generate_function_name(function_name=function_name, suffix=suffix)

        # Декораторы
        decorators_str = ""
        for d in self.decorators:
            decorators_str += f"@{d}\n"

        # Определения типа функции
        if self.asynchronous:
            function_type = 'async def'
        else:
            function_type = 'def'

        # Возвращаемая информация
        function_result = 'list'
        if result == 'void':
            function_result = 'None'

        # Генерация функции
        python_function = ""

        if decorators_str:
            python_function += decorators_str

        python_function += f"""{function_type} {function_name}(\n   {python_args}\n) -> {function_result}:
    return connection.fetch("SELECT * FROM {self.schema_name}.{function_name}({sql_args});", {funcion_args})
"""
        return python_function

    def generate(self) -> None:
        function_name_count = { }  # Для подсчета кол-во функций с одинаковым названием

        for function_name, _, sql_arguments, result in self.functions:
            if function_name in function_name_count:
                function_name_count[function_name] += 1
                suffix = function_name_count[function_name]
            else:
                function_name_count[function_name] = 1
                suffix = ""

            python_function = self.generate_python_function(
                function_name=function_name, sql_arguments=sql_arguments, result=result, suffix=suffix
            )
            self.python_functions.append(python_function)

        self.write_to_file()
        log.info(f"Generated {len(self.python_functions)} functions in {self.file_name}")

    # Запись в файл
    def write_imports_to_file(self, file):
        for i in self.imports:
            file.write(i + '\n')
        else:
            file.write('\n\n')

    def write_functions_to_file(self, file):
        for function in self.python_functions:
            file.write(function + '\n\n')

    def write_to_file(self) -> None:
        if self.path:
            file_path = os.path.join(self.path, self.file_name)

            if not os.path.exists(self.path):
                os.makedirs(self.path)
        else:
            file_path = self.file_name

        if not self.python_functions:
            exit(f"python_functions is {self.python_functions}")

        with open(file_path, 'w') as file:
            self.write_imports_to_file(file=file)
            self.write_functions_to_file(file=file)
