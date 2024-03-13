# Software Programming Quiz

The website is currently hosted in the OSU servers:
http://flip3.engr.oregonstate.edu:12118/

Please be on the OSU VPN in order to see and interact with the website.

INSTRUCTIONS TO LAUNCH LOCALLY:
Please follow instructions here to launch this locally: https://github.com/osu-cs340-ecampus/flask-starter-app 

You will need to have your own MariaDB database account, along with your info stored in .env to source the DDL.sql file as well.

You will also need to have a .env file according to instructions the flask-start app tutorial above to have the database working.

Please also make sure to have the dependencies required in requirements.txt in your venv to run the program.
To install depencies, do: pip install -r requirements.txt
To run the app, do: python3 app.py

CITATIONS:
For db_connector.py
Citation Scope: Based on flask-started-app database folder in github, from osu-cs340-ecampus , scope of code is the whole code in the source to setup the database connection, aka whole module below.
Date: January 25, 2024
Originality: Copied, we copied most of the osu-cs340-ecampus flask starter code, tweaked to our need.
We also followed their instructions for environment setup.
Below is from the starter code given to the class, CS 340, to use in capstone.
Source : https://github.com/osu-cs340-ecampus/flask-starter-app/blob/master/database/db_connector.py
