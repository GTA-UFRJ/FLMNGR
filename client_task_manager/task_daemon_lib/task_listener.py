import threading
from typing import Callable
import subprocess


class TaskMessageListener:
    """
    Interface for listen and forward bytes received from processes through a 
    two POSIX pipes to a handler function

    :param handler: function called every time a line (byte package) is received
    :type handler: Callable[[bytes],None]

    :param process: running subprocess which contains the write ends of sterr and stdout pipes
    :type process: subprocess.Popen
    """
    def __init__(self, handler:Callable[[bytes],None], process:subprocess.Popen):
        self.handler = handler
        self.thread = None
        self.process = process

    def _process_received_message(self, data:bytes):
        if data:
            try:
                self.handler(data)
            except Exception as e:
                # Lets define that untreatable messages don't cause crashing
                print("Task listener could not handle data. Let it go.")
        
    def _listen(self):
        while not self.exit_loop:
            stdout_output = self.process.stdout.readline()
            self._process_received_message(stdout_output) 
            
            stderr_output = self.process.stderr.readline()
            self._process_received_message(stderr_output) 
        
        self.process.stdout.close()
        self.process.stderr.close()
        self.process.wait()
    
    def start(self):
        """
        Creates a thread for listening pipes and forwarding bytes to handler

        :raises: Exception
        """
        # Don't know what errors can occur
        self.exit_loop = False
        self.thread = threading.Thread(target=self._listen)
        self.thread.start()

    def stop(self):
        """
        Stops the listening thread

        IMPORTANT NOTE:
        Depending on the received message, the handler function can kill the process
        and, therefore, kill this thread. This would cause a thread to terminate
        itself, which is not allowed (RuntimeError). This case is handled.

        :raises: Exception
        """
        self.exit_loop = True
        if self.thread:
            try:
                self.thread.join()
            except RuntimeError:
                print("Listener finished itself")
