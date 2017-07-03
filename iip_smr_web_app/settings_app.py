# -*- coding: utf-8 -*-

import json, os

""" Settings for iip_search_app. """


## solr ##

SOLR_URL = unicode( os.environ.get(u'IIP_SEARCH__SOLR_URL') )  # main solr instance


## auth ##

DEV_AUTH_HACK = unicode( os.environ.get(u'IIP_SEARCH__DEV_AUTH_HACK') )  # 'enabled' or 'disabled' (only enabled for local non-shib development)
LEGIT_ADMINS = json.loads( unicode(os.environ.get(u'IIP_SEARCH__LEGIT_ADMINS')) )  # json shib-eppn list
DB_USER = unicode( os.environ.get('IIP_SEARCH__DB_USER') )
DB_USER_PASSWORD = unicode( os.environ.get('IIP_SEARCH__DB_USER_PASSWORD') )

## misc ##

XML_DIR_PATH = unicode( os.environ.get(u'IIP_SEARCH__XML_DIR_PATH') )

URL_SCHEME = unicode( os.environ.get(u'IIP_SEARCH__URL_SCHEME') )  # 'http' or, on production, 'https'


## end
