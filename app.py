from flask import Flask,request
import sqlite3
from logging import Logger
import json

logger = Logger('app.log',10)

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
    return 'Hello, World!'

@app.route('/tasks',methods = ['GET',"POST"])
def tasks():
    if request.method == 'GET':
        query = "Select * from TASKS"
        try:
            cursor.execute(query)
        except Exception as e:
            logger.error(f"Query failed due to {e}")
            raise
        query_response = cursor.fetchall()
        logger.info("Query successful")
        return query_response
    elif request.method == 'POST':
        data =  request.get_json()
        task = data.get("task")
        status = data.get("status")

        query = f'''
                INSERT INTO TASKS (task,status) 
                VALUES (?,?)
                '''
        try:
            cursor.execute(query,(task,status))
            conn.commit()
        except Exception as e:
            logger.error(f"Query failed due to {e}")

        logger.info("Query Successful")

    return {"status":200}
        

    


if __name__ == '__main__':
    print(app)
    app.run(debug=True)