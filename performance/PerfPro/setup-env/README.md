# PerfPro Database Environment Setup Automation

This directory contains the automation scripts to setup the database environment for mongoDB. It includes installing mongo org and creating users accessing hosted Performance database.

## Directory Structure

1.  **run_db_env.sh**
    -   Executes the required steps to setup the mongodb.
    -   Uses other files for configurations and credentials.

2.  **mongo-release-info**
    -   Configuration template to setup a version.

3.  **db_info**
    -   Contains the database related information.
    -   It has `key = value` format.
    -   Only file need to be edited by user as per requirements.

4.  **create_user.js**
    -   Mongo script to create a user in database.

## Steps to setup

**_Note: use root user mode_**.

1.  Fill the db_info file template.
2.  Provide execution permission to run_db_env.sh file.
3.  Run the shell script using below options:
    -   To setup the environment only: `run_dev_env.sh`.
    -   To setup the enviornment with taking dump and restoring database: `run_dev_env.sh dump`.

## How to check

1.  Start mongoshell by typing `mongosh`.
2.  Execute the following command in mongoshell.
    1.  `show dbs`
    2.  `use database_name`
    3.  `show collections`
