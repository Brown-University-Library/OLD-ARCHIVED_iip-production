"""
WSGI config.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os, pprint, sys
import shellvars


# print( 'the initial env, ```{}```'.format( pprint.pformat(dict(os.environ)) ) )

PROJECT_DIR_PATH = os.path.dirname( os.path.dirname(os.path.abspath(__file__)) )
ENV_SETTINGS_FILE = os.environ['IIP_SMR__SETTINGS_PATH']  # set in `conf.d/passenger.conf`, and `env/bin/activate`

## update path
sys.path.append( PROJECT_DIR_PATH )

## Note: no need to activate the virtual-environment
## - the project's httpd/passenger.conf section allows specification of the python-path via `PassengerPython`, which auto-activates it
## - the auto-activation provides access to modules, but not, automatically, env-vars
## - env-vars loading under python3.x occurs via the `SenEnv` entry in the project's passenger.conf section
##   - requires apache env_module; info: <https://www.phusionpassenger.com/library/indepth/environment_variables.html>

## reference django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'  # so django can access its settings

## load up env vars
var_dct = shellvars.get_vars( ENV_SETTINGS_FILE )
for ( key, val ) in var_dct.items():
    os.environ[key.decode('utf-8')] = val.decode('utf-8')

# print( 'the final env, ```{}```'.format( pprint.pformat(dict(os.environ)) ) )

## gogogo
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
