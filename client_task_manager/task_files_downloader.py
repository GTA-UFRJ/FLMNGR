import requests
from requests.auth import HTTPBasicAuth
import os

class TaskDownloadGenericError(Exception):
    def __init__(self, complete_url:str, response):
        super().__init__(f"Failed to download from {complete_url}: {response.status_code} {response.reason}")

class TaskNotFoundInServer(Exception):
    def __init__(self, complete_url:str):
        super().__init__(f"Task not found in {complete_url}")

class TaskDownloadAuthFail(Exception):
    def __init__(self, complete_url:str):
        super().__init__(f"Could not authenticate when downloading from {complete_url}")

def _download_file(filename:str, complete_url:str, auth:HTTPBasicAuth):
    
    response = requests.get(complete_url, auth=auth, stream=True)

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"File '{filename}' downloaded successfully.")
    elif response.status_code == 404:
        raise TaskNotFoundInServer(complete_url)
    elif response.status_code == 401:
        raise TaskDownloadAuthFail(complete_url)
    else:
        raise TaskDownloadGenericError(complete_url, response)

def download_task_training_files(
    task_id:str,
    work_path:str,
    username:str, 
    password:str, 
    files_paths:list, 
    download_server_url:str):
    """
    Download files in list from a web server using credentials

    :param task_id: task ID 
    :type task_id: str

    :param work_path: path for client "tasks" dir, inside of which directories will be created for each task 
    :type work_path: str

    :param username: username used to download file
    :type username: str

    :param password: password used to download file
    :type password: str

    :param files_paths: files list
    :type files_paths: str

    :param download_server_url: URL in the format http://{hostname or IP}:{port}
    :type download_server_url: str

    :raises TaskDownloadGenericError: received status 50X, which suggests an internal server error

    :raises TaskDownloadAuthFail: invalid username and password
    
    :raises TaskNotFoundInServer: task files not found in server
    """
    
    task_path = os.path.join(work_path,f"task_{task_id}")
    if not os.path.exists(task_path):
        os.makedirs(task_path)

    for file_path in files_paths:
        local_filepath = os.path.join(task_path, file_path)
        url = f"{download_server_url}/download/{task_id}/{file_path}"
        auth = HTTPBasicAuth(username, password)
        _download_file(local_filepath, url, auth)
