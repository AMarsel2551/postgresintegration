import os, copy
from postgresintegration.database import DatabaseConnector
from postgresintegration.logger import log


class PostgresTableGenerator:
    def __init__(
            self,
            schema_name: str,
            file_name: str = None, path: str = None, imports: list = None,
            asynchronous: bool = False, decorators: list = None, arguments: str = None, prefix: str = None
    ):
        self.connector = DatabaseConnector(schema_name=schema_name)

        table = self.connector.get_postgres_table()
        new_table = {}
        for t in table:
            print(t)
            table_name = t[0]
            if table_name not in new_table:
                new_table[table_name] = {'table_name': table_name, 'data': []}
            new_table[table_name]['data'].append({
                "column_name": t[1],
                "column_type": t[2],
            })
        self.table = new_table

        self.schema_name = schema_name
        self.python_functions = []
        self.path = path
        self.file_name = file_name + '.py' or 'generated_functions.py'
        self.imports = list(set((imports or []) + ['from typing import Any\nfrom datetime import datetime']))
        self.arguments = list(set((arguments or []) + ['connection']))
        self.prefix = prefix
        self.decorators = decorators or []
        self.asynchronous = asynchronous

    def generate_function_name(self, table_name: str):
        if self.prefix is not None:
            function_name = f"{self.prefix}_{table_name}"
        else:
            function_name = f"{table_name}"

        return function_name

    def generate_funcrion_arguments(self, sql_arguments: list) -> [str, str, str]:
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
            "jsonb": "str",
            "json": "str",
            "bigint[]": "list[int]",
            "timestamp": "datetime",
            "date": "datetime"
        }
        python_args = copy.deepcopy(self.arguments)
        funcion_args = []
        sql_args = []

        for i, d in enumerate(sql_arguments, 1):
            column_name = d['column_name']
            column_type = d['column_type']

            arg_type = type_mapping.get(column_type)
            if arg_type is None:
                arg_type = 'Any'

            # python_args
            if column_name == 'global':
                column_name = f"v{column_name}"
            column_name_strip = column_name.strip('"')
            python_args.append(f"{column_name_strip}: {arg_type}=None")

            # funcion_args
            funcion_args.append(column_name_strip)

            # sql_args
            if i == 1:
                sql_args.append(f"where {column_name}=${i}")
            else:
                sql_args.append(f"and {column_name}=${i}")

        return ', '.join(python_args), ', '.join(funcion_args), ' '.join(sql_args)

    def generate_python_function(self, table_name: str, sql_arguments: list) -> str:
        # Аргументы для python функции (a, b, c) и ($1, $2, $3)
        python_args, funcion_args, sql_args = self.generate_funcrion_arguments(sql_arguments=sql_arguments)

        # Генерация названия функции
        function_name = self.generate_function_name(table_name=table_name)

        # Декораторы
        decorators_str = ""
        for d in self.decorators:
            decorators_str += f"@{d}\n"

        # Определения типа функции
        if self.asynchronous:
            function_type = 'async def'
        else:
            function_type = 'def'

        # Генерация функции
        python_function = ""

        if decorators_str:
            python_function += decorators_str

        python_function += f"""{function_type} {function_name}(\n   {python_args}\n) -> list:
    return connection.fetch("SELECT * FROM {self.schema_name}.{table_name} {sql_args};", {funcion_args})
"""
        return python_function

    def generate(self) -> None:
        for table_name in self.table:
            data = self.table[table_name]['data']
            python_function = self.generate_python_function(
                table_name=table_name, sql_arguments=data
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
