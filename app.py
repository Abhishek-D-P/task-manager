from flask import Flask,request, render_template,redirect
import sqlite3
import logging
import json
import os
import sys

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

query = ''' 
    CREATE TABLE IF NOT EXISTS tasks(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task VARCHAR(50) NOT NULL,
    status VARCHAR(50)
    );
    '''

cursor.execute(query)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/tasks',methods = ['GET',"POST",'PATCH','DELETE'])
def tasks():
    if request.method == 'GET':
        query = "Select * from TASKS"
        try:
            cursor.execute(query)
        except Exception as e:
            logging.error(f"Query failed due to {e}")
            raise
        all_tasks = cursor.fetchall()
        logging.info("Query successful")
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

    elif request.method == 'PATCH':
        response = request.get_json()
        id = response.get("id")
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
        payload = request.get_json()
        id = payload.get("id")
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
    
    return redirect("/tasks")

    
        


if __name__ == '__main__':
    app.run(debug=True)