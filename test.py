from main import PostgresFunctionGenerator

if __name__ == "__main__":
    generator = PostgresFunctionGenerator(
        schema_name="pim",
        prefix="db",
        asynchronous=True,
        # decorators=["testing(1)"],
        # path='database',
        file_name="generated_functions"
    )
    generator.generate()
