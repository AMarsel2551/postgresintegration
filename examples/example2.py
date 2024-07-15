from postgresintegration import PostgresTableGenerator

if __name__ == "__main__":
    generator = PostgresTableGenerator(
        schema_name="main",
        prefix="db",
        asynchronous=True,
        # decorators=["testing(1)"],
        # path='database',
        file_name="generated_functions"
    )
    generator.generate()
