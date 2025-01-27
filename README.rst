======
D0018E
======

Military Surplus Warehouse
==========================
- (*Name pending!*)

Student project for exploring the use and integration of databases in web developent with the help of tools like:

- Python_ 3.10+
- Flask_
- MySQL_

Setup
=====
To setup the site for testing and development, make sure your are on in the virtual enviroment. This will be displayed by the text *venv* appearing to the left of the cursor in a standard shell.

Otherwise run the following command from the root of the project folder:

Linux/WSL/MacOS
===============

.. code:: bash

    source bin/activate

And when wanting to exit the virtual environment, simply runt the following in the terminal:

.. code:: bash

    deactivate


Running/Testing
===============

To run the web application, type the following in the terminal:

.. code:: bash 

    flask run


Troubleshooting
===============

If there would be any problem with starting to use the *flask run* command, make sure the environment variable *FLASK_APP* is set to point at the starting/main file.

which otherwise can be fixed with:

.. code:: bash 
        
      export FLASK_APP=server



As the current implementation stands

Future plans
============

Future plans consists of changing the current hosting server that serves as more of testing ground to something more streamlined and solid along the lines of:

Waitress_ or Nginx_

.. _Nginx:    https://nginx.org/en/
.. _Waitress: https://flask.palletsprojects.com/en/stable/deploying/waitress/
.. _MySQL:    https://www.mysql.com/    
.. _Flask:    https://flask.palletsprojects.com/en/stable/
.. _Python:   https://www.python.org/downloads/
