import argparse
import duckdb
import asyncio
from rich.console import Console
from rich.table import Table
from app.utils.general import load_config

def get_db_path():
    """Gets the database path from the config file."""
    config = asyncio.run(load_config("config/config.yml"))
    return config["database"]

def list_tables(db_path):
    """Lists all tables in the database."""
    con = duckdb.connect(database=db_path, read_only=True)
    tables = con.execute("SHOW TABLES").fetchall()
    con.close()
    
    console = Console()
    if tables:
        rich_table = Table(title="Tables")
        rich_table.add_column("Table Name", style="cyan")
        for table in tables:
            rich_table.add_row(table[0])
        console.print(rich_table)
    else:
        console.print("No tables found in the database.")

def show_schema(db_path, table_name):
    """Shows the schema of a specific table."""
    con = duckdb.connect(database=db_path, read_only=True)
    try:
        schema = con.execute(f"PRAGMA table_info('{table_name}')").fetchall()
        con.close()
        
        console = Console()
        if schema:
            rich_table = Table(title=f"Schema for table: {table_name}")
            rich_table.add_column("Column Name", style="cyan")
            rich_table.add_column("Data Type", style="magenta")
            rich_table.add_column("Nullable", style="green")
            rich_table.add_column("Default", style="yellow")
            for column in schema:
                rich_table.add_row(str(column[1]), str(column[2]), str(bool(column[3])), str(column[4]))
            console.print(rich_table)
        else:
            console.print(f"Table '{table_name}' not found or has no columns.")
    except duckdb.CatalogException:
        console = Console()
        console.print(f"[bold red]Error:[/] Table '{table_name}' not found.")

def show_table(db_path, table_name, limit):
    """Shows the first N rows of a table."""
    con = duckdb.connect(database=db_path, read_only=True)
    try:
        data = con.execute(f"SELECT * FROM '{table_name}' LIMIT {limit}").fetchall()
        columns = [desc[0] for desc in con.description]
        con.close()
        
        console = Console()
        if data:
            rich_table = Table(title=f"Top {limit} rows from table: {table_name}")
            for col in columns:
                rich_table.add_column(col, style="cyan")
            for row in data:
                rich_table.add_row(*[str(item) for item in row])
            console.print(rich_table)
        else:
            console.print(f"Table '{table_name}' is empty or does not exist.")
    except duckdb.CatalogException:
        console = Console()
        console.print(f"[bold red]Error:[/] Table '{table_name}' not found.")


def execute_query(db_path, query):
    """Executes a given SQL query and prints the result."""
    con = duckdb.connect(database=db_path, read_only=True)
    try:
        result = con.execute(query).fetchall()
        columns = [desc[0] for desc in con.description]
        con.close()

        console = Console()
        if result:
            rich_table = Table(title="Query Result")
            for col in columns:
                rich_table.add_column(col, style="cyan")
            for row in result:
                rich_table.add_row(*[str(item) for item in row])
            console.print(rich_table)
        else:
            console.print("Query executed successfully, but returned no results.")
    except (duckdb.ParserException, duckdb.BinderException, duckdb.CatalogException) as e:
        console = Console()
        console.print(f"[bold red]Error executing query:[/] {e}")


def main():
    parser = argparse.ArgumentParser(description="DuckDB Database Explorer.")
    db_path = get_db_path()

    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    subparsers.required = True

    # 'tables' command
    parser_tables = subparsers.add_parser('tables', help='List all tables in the database.')
    parser_tables.set_defaults(func=lambda args: list_tables(db_path))

    # 'schema' command
    parser_schema = subparsers.add_parser('schema', help='Show the schema of a specific table.')
    parser_schema.add_argument('table_name', type=str, help='The name of the table.')
    parser_schema.set_defaults(func=lambda args: show_schema(db_path, args.table_name))

    # 'show' command
    parser_show = subparsers.add_parser('show', help='Show the first N rows of a table.')
    parser_show.add_argument('table_name', type=str, help='The name of the table.')
    parser_show.add_argument('--limit', type=int, default=10, help='Number of rows to display.')
    parser_show.set_defaults(func=lambda args: show_table(db_path, args.table_name, args.limit))

    # 'query' command
    parser_query = subparsers.add_parser('query', help='Execute a custom SQL query.')
    parser_query.add_argument('sql_query', type=str, help='The SQL query to execute.')
    parser_query.set_defaults(func=lambda args: execute_query(db_path, args.sql_query))

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main() 