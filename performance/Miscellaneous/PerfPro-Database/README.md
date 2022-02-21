## PerfPro-Database

- Automates the development environment for mongodb on the system.

# File Structure of PerfPro-Database

1) run_db_env.sh 
 - It is a shell script.
 - Executes the required steps to setup the mongodb.
 - uses other files for configurations and credentials.

2) mongo-release-info
 - Configuration template to setup a version.

3) db_info
 - Contains the database related information
 - It has 'key = value' format.
 - only file need to be edited by user as per requirements.

4) create_user.js
 - mongo script to create a user in database.


# Steps to setup

Note: use root user mode.

1) Fill the db_info file template.
2) Provide execution permission to run_db_env.sh file.
3) run the shell script using below options:-
 - To setup the environment only: run_dev_env.sh
 - To setup the enviornment with taking dump and restoring database: run_dev_env.sh dump


# How to check
1) start mongoshell by typing 'mongosh'.
2) Execute the following command in mongoshell.
 - show dbs
 - use database_name
 - show collections
