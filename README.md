## Overview

This is the code for the student developer version of the iip project


---

### Student-Developer Installation

- make a dir `iip_student_dev_stuff`
- cd into that dir
- $ python3 -m venv ./env3_iip_student_dev_project
- $ git clone https://github.com/Brown-University-Library/iip_smr_web_project.git ./iip_student_dev_project
- $ mkdir ./settings
- $ mkdir ./logs
- $ mkdir ./db
- $ mkdir ./pull_from_github.sh
- $ cd ./iip_student_dev_project
- $ source ../env3_iip_student_dev_project/bin/activate
- $ pip install --upgrade pip
- $ pip install -r ./iip_smr_config/requirements.txt
- put submitted settings file in the settings dir
- put submitted db file in the db dir
- point the env/bin/activate file to the envar_settings.sh file
- go through the settings file, updating all paths
- $ python ./manage.py check
- $ python ./manage.py runserver
