import sqlite3

conn = sqlite3.connect('tasks.db',check_same_thread=False)
cursor = conn.cursor()

# migrate the changes in db 

# define changes
table_name = 'users'
new_table_name = table_name + '_new'

# create new table
print(f'Creating new table {new_table_name} {'.'*50}')
new_schema = f'CREATE TABLE IF NOT EXISTS {new_table_name}(id INTEGER PRIMARY KEY AUTOINCREMENT,username VARCHAR(50) UNIQUE NOT NULL,name VARCHAR(50) NOT NULL,password_hash VARCHAR(255) NOT NULL,role VARCHAR(50));'

cursor.execute(new_schema)
conn.commit()
print(f'New table {new_table_name} Created!')

# copy the old table to new
print(f'copying data from {table_name} to new table {new_table_name} {'.'*50}')
copy_table = f'ALTER TABLE {new_table_name} VALUES(SELECT * FROM {table_name})'
cursor.execute(new_schema)
conn.commit()
print(f'Copying successful!')



# delete old table
print(f'Deleting old table {table_name} {'.'*50}')

conn.execute("PRAGMA foreign_keys = OFF")
delete_table = f'DROP TABLE {table_name};'
cursor.execute(delete_table)
conn.execute("PRAGMA foreign_keys = ON")

conn.commit()

print(f'Successfully deleted {table_name}!')


# rename table
print(f'Renaming table {new_table_name}  to {table_name}{'.'*50}')

rename_table = f'ALTER TABLE {new_table_name} RENAME TO {table_name};'
cursor.execute(rename_table)
conn.commit()
print(f'Renamed!')
print("Migration successful!")