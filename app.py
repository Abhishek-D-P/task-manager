from flask import Flask,request, render_template,redirect,jsonify
import sqlite3
import logging
import json
import os
import sys
from werkzeug.security import generate_password_hash,check_password_hash
import secrets
import time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Directs logs to console stream
    ]
)

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
conn = sqlite3.connect(BASE_DIR / 'tasks.db', check_same_thread=False)
cursor = conn.cursor()

SESSION_DURATION_MINUTES = float(os.environ.get('SESSION_DURATION_MINUTES','1'))

with open(BASE_DIR / 'query.json') as f:
    queries = json.load(f)

conn.execute("PRAGMA foreign_keys = ON")
cursor.execute(queries.get("create_users_table"))
cursor.execute(queries.get("create_tasks_table"))

sessions = {}

def get_current_user_id():
    '''
        Returns user and role from session id
    '''

    session_id = request.cookies.get('session_id',None)
    if session_id:
        session = sessions.get(session_id)
        if session:
            session_expiry = session.get('expires_at')
            if time.time() <= session_expiry:
                user = session.get('user_id')
                role = session.get('role')
                return 'valid',user,role      
            else:
                logging.warning("Session expired. Removing session.")
                sessions.pop(session_id)
        else:
            logging.warning("Session ID not found in sessions dictionary.")
    else:
        logging.warning("No session ID found in cookies.")
    return "expired",None, None
            

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
            if not user or not check_password_hash(user[3],password):    
                raise ValueError  
            session_id = secrets.token_hex(32)
            session_expires_at = time.time() + SESSION_DURATION_MINUTES * 60
            logging.debug(f"Session created for user_id {user[0]} with session_id {session_id} expiring in {SESSION_DURATION_MINUTES} minutes.")
            sessions[session_id] = {'user_id':user[0],'role':user[4],'expires_at':session_expires_at}
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

    response = redirect("/tasks")
    response.set_cookie("session_id",session_id,httponly=True)
    return response

@app.route('/logout',methods = ['GET'])
def logout():
    session_id = request.cookies.get('session_id')
    try:
        sessions.pop(session_id)
    except:
        pass
    response = redirect('/')
    response.delete_cookie('session_id')
    return response
        

@app.route('/tasks',methods = ['GET',"POST"])
def tasks():
    session_status , user_id, role = get_current_user_id()
    print(role)
    if session_status == 'expired' or user_id is None:
        response = redirect('/')
        response.delete_cookie('session_id')
        return response
    if request.method == 'GET':
        query = queries.get("get_tasks")
        try:
            if role == 'admin':
                cursor.execute('SELECT * FROM TASKS')
            else:
                cursor.execute(query,(user_id,))
        except Exception as e:
            logging.error(f"Query failed due to {e}")
            raise
        all_tasks = cursor.fetchall()
        print(all_tasks)
        logging.info("Get query successful")
        return render_template('task.html',title="Tasks Page", tasks=all_tasks, role=role)
    elif request.method == 'POST':
        task = request.form.get("task")
        status = request.form.get("status")
        query = queries.get("create_task")
        try:
            cursor.execute(query,(task,status,user_id))
            conn.commit()
        except Exception as e:
            logging.error(f"Query failed due to {e}")
        logging.info("Posted Successful")

    return redirect("/tasks")

@app.route("/tasks/<int:id>",methods = ['PATCH','DELETE'])
def task_item(id):
    session_status , user_id, role = get_current_user_id()
    if session_status == 'expired' or user_id is None:
        return redirect('/')
    if request.method == 'PATCH':
        response = request.get_json()
        task = response.get("task")
        status = response.get("status")
        if role == "admin":
            query = queries.get("update_task_admin")
        else:
            query = queries.get("update_task")
        try:
            if role == 'admin':
                cursor.execute(query,(task,status,id))
            else:
                cursor.execute(query,(task,status,id,user_id))
            conn.commit()
        except Exception as e:
            logging.error(f"Query Failed due to {e}")
            return {"success": False, "message": "Internal server error"}, 500
        logging.info("Updated!")
        return {"success":True},200
    
    elif request.method == 'DELETE':
        if role == "admin":
            query = queries.get("delete_task_admin")
        else:
            query = queries.get("delete_task")
        
        try:
            if role == 'admin':
                cursor.execute(query,(id,))
            else:
                cursor.execute(query,(id,user_id))
            conn.commit()
            logging.info("Delete successful!")
        except Exception as e:
            logging.error(f"Delete failed due to {e}")
            return {"success": False, "message": "Internal server error"}, 500
        return {"success":True},200




if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=5000)