# -*- coding: utf-8 -*-

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
