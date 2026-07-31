from flask import Flask,request, render_template,redirect
import sqlite3
import logging
from logging import Logger
import json
import os

logging.basicConfig()
logger = Logger(os.path.join(os.getcwd(),'app.log'),10)

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

@app.route('/tasks',methods = ['GET',"POST",'DELETE'])
def tasks():
    if request.method == 'GET':
        query = "Select * from TASKS"
        try:
            cursor.execute(query)
        except Exception as e:
            logger.error(f"Query failed due to {e}")
            raise
        all_tasks = cursor.fetchall()
        print(all_tasks)
        logger.info("Query successful")
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
            logger.error(f"Query failed due to {e}")
        logger.info("Posted Successful")
    elif request.method == 'DELETE':
        payload = request.get_json()
        id = payload.get("id")
        print(id)
        query = f'''
                DELETE FROM TASKS 
                WHERE id = ?
                '''
        try:
            cursor.execute(query,(id,))
            conn.commit()
            logger.info("Delete successful!")
        except Exception as e:
            logger.error(f"Delete failed due to {e}")
            return {"success": False, "message": "Internal server error"}, 500

        return {"success":True},200
    return redirect("/tasks")

    
        


if __name__ == '__main__':
    print(app)
    app.run(debug=True)