from flask import Flask,request, render_template,redirect,jsonify
import sqlite3
import logging
import json
import os
import sys
from werkzeug.security import generate_password_hash,check_password_hash

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Directs logs to console stream
    ]
)

app = Flask(__name__)
conn = sqlite3.connect('tasks.db',check_same_thread=False)
cursor = conn.cursor()

with open('query.json') as f:
    queries = json.load(f)

conn.execute("PRAGMA foreign_keys = ON")
cursor.execute(queries.get("create_users_table"))
cursor.execute(queries.get("create_tasks_table"))


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register',methods = ['GET',"POST"])
def register():
    if request.method == 'GET':
        return render_template('register.html',title="Register")
    elif request.method == 'POST':
        username = request.form.get("username")
        name = request.form.get("name")
        password = request.form.get("password")
        password_hash = generate_password_hash(password)

        query = queries.get("create_users")
        try:
            cursor.execute(query,(username,name,password_hash))
            conn.commit()
        except Exception as e:
            logging.error(f"Query failed due to {e}")
            raise
        logging.info("Posted Successful")

    return redirect("/login")

@app.route('/login',methods = ['GET',"POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        query = queries.get("get_user")

        try:
            cursor.execute(query,(username,))
            user = cursor.fetchone()
            if user or not check_password_hash(user[2],password):    
                raise ValueError    
        except ValueError:
            logging.error("Wrong username or password")
            return jsonify({
            "status": "error",
            "message": "Invalid email or password."
        }), 401 

        except Exception as e:
            logging.error(f"Query failed due to {e}")
            raise
        logging.info("Logged in Successful")

    return redirect("/tasks")


@app.route('/tasks',methods = ['GET',"POST"])
def tasks():
    if request.method == 'GET':
        query = "Select * from TASKS"
        try:
            cursor.execute(query)
        except Exception as e:
            logging.error(f"Query failed due to {e}")
            raise
        all_tasks = cursor.fetchall()
        logging.info("Get query successful")
        return render_template('task.html',title="Tasks Page", tasks=all_tasks)
    elif request.method == 'POST':
        task = request.form.get("task")
        status = request.form.get("status")

        query = f'''
                INSERT INTO TASKS (task,status) 
                VALUES (?,?)
                '''
        try:
            cursor.execute(query,(task,status))
            conn.commit()
        except Exception as e:
            logging.error(f"Query failed due to {e}")
        logging.info("Posted Successful")

    return redirect("/tasks")

@app.route("/tasks/<int:id>",methods = ['PATCH','DELETE'])
def task_item(id):
    print("in")
    if request.method == 'PATCH':
        response = request.get_json()
        task = response.get("task")
        status = response.get("status")
        query = '''
        UPDATE TASKS 
        SET task = ?, status = ?
        where id = ?
        '''
        try:
            cursor.execute(query,(task,status,id))
            conn.commit()
        except Exception as e:
            logging.error(f"Query Failed due to {e}")
            return {"success": False, "message": "Internal server error"}, 500
        logging.info("Updated!")
        return {"success":True},200
    
    elif request.method == 'DELETE':
        query = f'''
                DELETE FROM TASKS 
                WHERE id = ?
                '''
        try:
            cursor.execute(query,(id,))
            conn.commit()
            logging.info("Delete successful!")
        except Exception as e:
            logging.error(f"Delete failed due to {e}")
            return {"success": False, "message": "Internal server error"}, 500
        return {"success":True},200
        


if __name__ == '__main__':
    app.run(debug=True)