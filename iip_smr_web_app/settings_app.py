# -*- coding: utf-8 -*-

import json, os

""" Settings for iip_smr_web_app. """


## solr ##

SOLR_URL = os.environ['IIP_SEARCH__SOLR_URL']  # main solr instance


## auth ##

DEV_AUTH_HACK = os.environ[u'IIP_SEARCH__DEV_AUTH_HACK']  # 'enabled' or 'disabled' (only enabled for local non-shib development)
LEGIT_ADMINS = json.loads( os.environ['IIP_SEARCH__LEGIT_ADMINS'] )  # json shib-eppn list
DB_USER = os.environ['IIP_SEARCH__DB_USER']
DB_USER_PASSWORD = os.environ['IIP_SEARCH__DB_USER_PASSWORD']

## misc ##

XML_DIR_PATH = os.environ['IIP_SEARCH__XML_DIR_PATH']

URL_SCHEME = os.environ['IIP_SEARCH__URL_SCHEME']  # 'http' or, on production, 'https'


## end
