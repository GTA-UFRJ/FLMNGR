Flower Tasks Daemon Library (FTDL)
===================================

This is a library for starting a Flower task as a child process. It also receives information from this task for logging and for finishing the task.
The task initializers uppon execution, create a Flower child process that reports message to the task initializer using a UDP socket (client is the task reporter and server is the task listener).

Task
-----

.. automodule:: task_daemon_lib.task
   :members:

Client-side task
-----------------

.. automodule:: task_daemon_lib.client_side_task
   :members:

Server-side task
-----------------

.. automodule:: task_daemon_lib.server_side_task
   :members:

Task listener
--------------

.. automodule:: task_daemon_lib.task_listener
   :members:

Task reporter
--------------

.. automodule:: task_daemon_lib.task_reporter
   :members:

Task exceptions
----------------

.. automodule:: task_daemon_lib.task_exceptions
   :members:

