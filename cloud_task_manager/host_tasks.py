from flask import Flask, request, send_from_directory, abort
import os
from tasks_db_interface import *
from pathlib import Path
import sys

class HostTasksManager:
    def __init__(
        self,
        work_path:str) -> None:

        self.upload_folder = os.path.join(work_path,'tasks')
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
        print(f"Folder: {self.upload_folder}")

        self.tasks_db_interface = TasksDbInterface(work_path)

    def _get_tasks_cred(self, task_id:str):
        tasks_info = self.tasks_db_interface.query_task(task_id)
        return tasks_info['username'], tasks_info['password']
    
    def authenticate(self, received_task_id:str, received_auth):
        db_username, db_password = self._get_tasks_cred(received_task_id)
        return received_auth and (received_auth.username == db_username and received_auth.password == db_password)
    
app = Flask(__name__)

@app.route('/download/<task>/<filename>', methods=['GET'])
def download_file(task, filename):
    """Serve a file for download."""
    ctx = HostTasksManager(sys.argv[1])
    try:
        if not ctx.authenticate(task, request.authorization):
            return unauthorized_response()
    except TaskNotRegistered as e:
        return task_not_registered_response()

    task_folder = os.path.join(ctx.upload_folder, f"task_{task}")
    print(f"File: {os.path.join(task_folder, filename)}")
    
    return send_from_directory(task_folder, filename, as_attachment=True)

def unauthorized_response():
    """Send a 401 Unauthorized response."""
    return (
        "Unauthorized access. Please provide valid credentials.",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )

def task_not_registered_response():
    return (
        "File not found",
        404,
        {},
    )

if __name__ == '__main__':
    app.run(debug=True)
