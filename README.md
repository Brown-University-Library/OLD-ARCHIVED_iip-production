## Overview

This is the code for the production iip project.


---

### Installation

- make a dir `iip_webapp_stuff`
- cd into that dir
- $ python3 -m venv ./env3_iip_web
- $ git clone https://github.com/Brown-University-Library/iip_production.git ./iip_web_project
- $ mkdir ./settings
- $ mkdir ./logs
- $ mkdir ./db
- $ mkdir ./pull_from_github
- $ cd ./iip_web_project
- $ source ../env3_iip_web/bin/activate
- $ pip install --upgrade pip
- $ pip install -r ./config/requirements.txt
- put submitted settings file in the settings dir
    - watch for line-endings
- put submitted db file in the db dir
- point the env/bin/activate file to the envar_settings.sh file
    - give lines for bottom
    - give deactivate line
- go through the settings file, updating all paths
- $ python ./manage.py check
- $ python ./manage.py runserver
