# -*- coding: utf-8 -*-

import json, os

""" Settings for iip_smr_web_app. """


## solr ##

SOLR_URL = os.environ['IIP_SMR__SOLR_URL']  # main solr instance


## auth ##

DEV_AUTH_HACK = os.environ[u'IIP_SMR__DEV_AUTH_HACK']  # 'enabled' or 'disabled' (only enabled for local non-shib development)
LEGIT_ADMINS = json.loads( os.environ['IIP_SMR__LEGIT_ADMINS'] )  # json shib-eppn list
DB_USER = os.environ['IIP_SMR__DB_USER']
DB_USER_PASSWORD = os.environ['IIP_SMR__DB_USER_PASSWORD']


## misc ##

XML_DIR_PATH = os.environ['IIP_SMR__XML_DIR_PATH']

IIP_SMR__XML_DIR_URL = os.environ['IIP_SMR__XML_DIR_URL']

URL_SCHEME = os.environ['IIP_SMR__URL_SCHEME']  # 'http' or, on production, 'https'

DOCUMENTATION_URL = os.environ['IIP_SMR__DOCUMENTATION_URL']

LATIN_CSV_URL = "https://raw.githubusercontent.com/Brown-University-Library/iip-word-lists/master/new-version/corrected_latin.csv"
LATIN_CSV_NEW_URL = "https://raw.githubusercontent.com/Brown-University-Library/iip-word-lists/master/new-version/Step%204%20New%20Output.csv"

## proxy ##

FETCH_DIR_URL= os.environ['IIP_SMR__FETCH_URL_ROOT_DIR']
if FETCH_DIR_URL[-1:] is not '/':  # since the server may or may not result in the '/', let's make the setting predictable
    FETCH_DIR_URL = '%s/' % FETCH_DIR_URL


## end ##
