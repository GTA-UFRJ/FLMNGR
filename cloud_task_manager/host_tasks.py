from flask import Flask, request, send_from_directory, abort, jsonify
from flask_cors import CORS
import os
from cloud_task_manager.tasks_db_interface import *
from pathlib import Path
import sys
from werkzeug.datastructures import Authorization
from flask.wrappers import Response
import configparser

configs = configparser.ConfigParser()
configs.read("./config.ini")
hostname = configs["server.broker"]["host"]

class HostTasksManager:
    '''
    Verify task info for download

    :param work_path: path to the directory where "tasks" directory is inside
    :type work_path: str
    '''
    def __init__(self, work_path: str) -> None:
        self.upload_folder = os.path.join(work_path, 'tasks')
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
        print(f"Folder: {self.upload_folder}")

        self.tasks_db_interface = TasksDbInterface(work_path)

    def _get_tasks_cred(self, task_id: str):
        tasks_info = self.tasks_db_interface.query_task(task_id)
        return tasks_info['username'], tasks_info['password']
    
    def authenticate(self, received_task_id: str, received_auth:Authorization)->bool:
        '''
        Check credentials for downloading a task

        :param received_task_id: ID of the task to search in the database
        :type received_task_id: str

        :param received_auth: authorization containing username and password send in HTTP
        :type received_auth: werkzeug.datastructures.Authorization

        :return: True if credentials in request matches credentials in database
        :rtype: bool 

        :raises sqlite3.IntegrityError: could not perform DB statement

        :raises TaskNotRegistered: task not found in DB
        '''
        db_username, db_password = self._get_tasks_cred(received_task_id)
        return received_auth and (received_auth.username == db_username and received_auth.password == db_password)
    
app = Flask(__name__)
CORS(app)  # Habilita CORS para toda a aplicação

@app.route('/download/<task>/<filename>', methods=['GET'])
def download_file(task:str, filename:str)->Response:
    '''
    Executes uppon reception of http://127.0.0.1:8080/download/xxxx/file.py (GET) where xxxx is the task id

    :param task: task ID
    :type task: str

    :param filename: filename
    :type filename: str

    :return: response
    :rtype: flask.wrappers.Response
    '''
    ctx = HostTasksManager(sys.argv[1])
    try:
        if not ctx.authenticate(task, request.authorization):
            return _unauthorized_response()
    except (TaskNotRegistered, sqlite3.IntegrityError):
        return _task_not_registered_response()

    task_folder = os.path.join(ctx.upload_folder, f"task_{task}")
    print(f"File: {os.path.join(task_folder, filename)}")
    
    return send_from_directory(task_folder, filename, as_attachment=True)

@app.route('/upload_files', methods=['POST'])
def upload_files()->Response:
    '''
    Executes uppon reception of http://127.0.0.1:8080/upload_files (POST)

    :return: response
    :rtype: flask.wrappers.Response
    '''
    ctx = HostTasksManager(sys.argv[1])
    
    task_id = request.form.get("task_id")
    if not task_id:
        return jsonify({"error": "Task ID is required"}), 400

    task_folder = os.path.join(ctx.upload_folder, f"task_{task_id}")
    os.makedirs(task_folder, exist_ok=True)

    uploaded_files = request.files.getlist("files")
    if not uploaded_files:
        return jsonify({"error": "No files uploaded"}), 400

    saved_files = []
    for file in uploaded_files:
        file_path = os.path.join(task_folder, file.filename)
        file.save(file_path)
        saved_files.append(file.filename)
    
    return jsonify({"message": "Files uploaded successfully", "files": saved_files}), 200

def _unauthorized_response():
    """Send a 401 Unauthorized response."""
    return (
        jsonify({"error": "Unauthorized access. Please provide valid credentials."}),
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )

def _task_not_registered_response():
    return (
        jsonify({"error": "Task not found"}),
        404,
        {},
    )

if __name__ == '__main__':
    app.run(host=hostname, debug=True)
