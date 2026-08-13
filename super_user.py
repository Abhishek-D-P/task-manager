import argparse
import json
from werkzeug.security import generate_password_hash
import sqlite3

conn = sqlite3.connect('tasks.db',check_same_thread=False)
cursor = conn.cursor()

with open('query.json','r') as f:
    queries = json.load(f)
parser = argparse.ArgumentParser(description='Create super user')
parser.add_argument('--username',default='admin')
parser.add_argument('--name',required=True)
parser.add_argument('--password',default='admin')
args = parser.parse_args()

username = args.username
name = args.name
password = args.password
password_hash = generate_password_hash(password)
role = 'admin'
cursor.execute(queries.get('create_users'),(username,name,password_hash,role))
conn.commit()

print(f"Create super user with username: {username} and password: {password}")