from flask import Flask, request, send_from_directory, abort, jsonify
from flask_cors import CORS
import os
from cloud_task_manager.tasks_db_interface import *
from pathlib import Path
import sys

class HostTasksManager:
    def __init__(self, work_path: str) -> None:
        self.upload_folder = os.path.join(work_path, 'tasks')
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
        print(f"Folder: {self.upload_folder}")

        self.tasks_db_interface = TasksDbInterface(work_path)

    def _get_tasks_cred(self, task_id: str):
        tasks_info = self.tasks_db_interface.query_task(task_id)
        return tasks_info['username'], tasks_info['password']
    
    def authenticate(self, received_task_id: str, received_auth):
        db_username, db_password = self._get_tasks_cred(received_task_id)
        return received_auth and (received_auth.username == db_username and received_auth.password == db_password)
    
app = Flask(__name__)
CORS(app)  # Habilita CORS para toda a aplicação

@app.route('/download/<task>/<filename>', methods=['GET'])
def download_file(task, filename):
    """Serve a file for download."""
    ctx = HostTasksManager(sys.argv[1])
    try:
        if not ctx.authenticate(task, request.authorization):
            return unauthorized_response()
    except TaskNotRegistered:
        return task_not_registered_response()

    task_folder = os.path.join(ctx.upload_folder, f"task_{task}")
    print(f"File: {os.path.join(task_folder, filename)}")
    
    return send_from_directory(task_folder, filename, as_attachment=True)

@app.route('/upload_files', methods=['POST'])
def upload_files():
    """Handle file uploads."""
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

def unauthorized_response():
    """Send a 401 Unauthorized response."""
    return (
        jsonify({"error": "Unauthorized access. Please provide valid credentials."}),
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )

def task_not_registered_response():
    return (
        jsonify({"error": "File not found"}),
        404,
        {},
    )

if __name__ == '__main__':
    app.run(debug=True)