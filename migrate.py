import sqlite3
from pathlib import Path


def quote_identifier(identifier):
    """Quote a SQLite identifier after validating it is a non-empty string."""
    if not isinstance(identifier, str) or not identifier:
        raise ValueError('SQLite identifiers must be non-empty strings')
    return '"' + identifier.replace('"', '""') + '"'

BASE_DIR = Path(__file__).resolve().parent
conn = sqlite3.connect(BASE_DIR / 'tasks.db', check_same_thread=False)
cursor = conn.cursor()

# migrate the changes in db 

def migrate_table(table_name, column_name=None, column_attributes=None):
    """Recreate a table while deriving its existing columns automatically.

    ``column_name`` and ``column_attributes`` can be used to add a column to
    the copied schema, for example ``('role', "VARCHAR(20) NOT NULL DEFAULT
    'user'")``.
    """
    table = quote_identifier(table_name)
    new_table = quote_identifier(f'{table_name}_new')

    columns = cursor.execute(f'PRAGMA table_info({table})').fetchall()
    if not columns:
        raise ValueError(f'Table {table_name!r} does not exist or has no columns')

    definitions = []
    column_names = []
    for _, name, data_type, not_null, default_value, primary_key in columns:
        definition = f'{quote_identifier(name)} {data_type or ""}'.strip()
        if primary_key:
            definition += ' PRIMARY KEY'
        if not_null:
            definition += ' NOT NULL'
        if default_value is not None:
            definition += f' DEFAULT {default_value}'
        definitions.append(definition)
        column_names.append(quote_identifier(name))

    if column_name is not None:
        if column_name in {column[1] for column in columns}:
            raise ValueError(f'Column {column_name!r} already exists')
        if not column_attributes:
            raise ValueError('column_attributes is required for a new column')
        definitions.append(f'{quote_identifier(column_name)} {column_attributes}')

    try:
        print(f'Creating new table {table_name}_new {"." * 50}')
        conn.execute('PRAGMA foreign_keys = OFF')
        cursor.execute(f'CREATE TABLE {new_table} ({", ".join(definitions)})')
        print(f'New table {table_name}_new Created!')

        print(f'Copying data from {table_name} to new table {table_name}_new {"." * 50}')
        target_columns = ', '.join(column_names)
        cursor.execute(
            f'INSERT INTO {new_table} ({target_columns}) '
            f'SELECT {target_columns} FROM {table}'
        )
        print('Copying successful!')

        print(f'Deleting old table {table_name} {"." * 50}')
        cursor.execute(f'DROP TABLE {table}')
        print(f'Successfully deleted {table_name}!')

        print(f'Renaming table {table_name}_new to {table_name} {"." * 50}')
        cursor.execute(f'ALTER TABLE {new_table} RENAME TO {table}')
        conn.commit()
        print('Renamed!')
        print('Migration successful!')
    except Exception:
        conn.rollback()
        cursor.execute(f'DROP TABLE IF EXISTS {new_table}')
        conn.commit()
        raise
    finally:
        conn.execute('PRAGMA foreign_keys = ON')

migrate_table('tasks')
migrate_table('users')