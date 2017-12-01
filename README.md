## Overview

This is a stripped-down version of the code for the [Inscriptions of Israel/Palestine Project](http://library.brown.edu/cds/projects/iip/) project.


---

### Student-Developer Installation

- First:

  - Make sure you have Python and the virtualenv program (these come installed on Macs). You can verify this by entering `python --version` into the terminal.

  - Make sure you have Brown's VPN software installed.

- Change directory in to the "env_iip/" folder. Run `./setup.sh`. This should create three folders, bin, include, and lib, and install a new version of python in this folder.

  - if that doesn't work, you can run these commands directly from the env_iip folder (not sure what the Windows equivalent of these are):

    - `virtualenv --python=/usr/bin/python2.7 --prompt=[iip] --no-site-packages ./`

    - ``echo source `pwd`/variables.sh >> bin/activate``

- The "variables.sh" file can be used to change lots of settings, but you won't need to touch it for now.

- Change directory to the main "iip_dev/" folder.

- On Mac/Linux, run `source env_iip/bin/activate`. On Windows, run `env_iip\bin\activate.bat`. Your command prompt should now start with `[iip]`.

  - this loads the new version of python and sets your terminal to use that one instead of your system version.

- Change directory to the "project/" folder.

- Install the dependencies for the project. Run `pip install -r iip_config/requirements.txt`

- Set up the database. Still in the "project/" folder, run `python ./manage.py syncdb`

  - follow the prompts to create a database user

- Run the project! Log in to Brown's VPN and then run `python ./manage.py runserver`

- go to http://localhost:8000/search to view the project.

### Running Normally

When you don't need to set up the whole project, all you need to do is `source env_iip/bin/activate` and then change directory into "project/" and run `python ./manage.py runserver`.

### Questions?
Ask Carlos, for now. You can email or gchat him at carlos_rotger@brown.edu (or starting June 15, carlos_rotger@alumni.brown.edu)
