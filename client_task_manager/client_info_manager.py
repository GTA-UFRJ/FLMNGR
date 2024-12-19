from pathlib import Path
import os
import json

class ClientInfoManager:
    """
    Stores in disk and retrieves from disk client info

    :param workpath: project location, within which "client_info" dir will reside
    :type workpath: str
    """
    def __init__(self, work_path:str, id:str) -> None:
        client_info_dir_path = os.path.join(work_path, 'client_info')
        Path(client_info_dir_path).mkdir(parents=True, exist_ok=True)
        
        self.client_info_file_path = os.path.join(client_info_dir_path, f'{id}_info.json')
        
        self.has_changed = False

    def get_info(self)->dict:
        """
        Returns JSON read from "{workpath}/client_info/info.json"
        
        :return: JSON with client info or None
        :rtype: dict 

        :raises: FileNotFoundError

        :raises: JSONDecodeError
        """
        with open(self.client_info_file_path,'r') as f:
            complete_info = json.load(f)
        return {k: v for k, v in complete_info.items() if v is not None}
    
    def get_info_if_changed(self)->dict:
        """
        Returns not None client info only if it has changed since last call of this method
        
        :return: JSON with client info or None
        :rtype: dict 

        :raises: FileNotFoundError

        :raises: JSONDecodeError
        """
        if self.has_changed:
            self.has_changed = False
            return self.get_info()
        else:
            return None
        
    def save_complete_info(self, client_info:dict):
        """
        Store all client info at "{workpath}/client_info/info.json"
        
        :param client_info: JSON with client info
        :type client_info: dict 

        :raises: FileNotFoundError
        """
        with open(self.client_info_file_path,'w') as f:
            json.dump(client_info, f)
            self.has_changed = True
            
    def update_info(self, client_info_to_change:dict):
        """
        Change some client info, mantaining the other as they are

        :param client_info_to_change: JSON with just client info that may change
        :type client_info_to_change: dict 

        :raises: FileNotFoundError

        :raises: JSONDecodeError
        """
        if client_info_to_change is None:
            return
        
        old_info = self.get_info()

        updated_info = old_info
        for key, value in client_info_to_change.items():
            if key in old_info:
                updated_info[key] = value
        
        self.save_complete_info(updated_info)
