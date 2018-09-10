# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging, os, subprocess
from django.conf import settings
from iip_smr_web_app import settings_app


log = logging.getLogger(__name__)


class Versioner( object ):
    """ Contains functions for accessing github xml file and propogating cache info.
        Helper for views.view_xml() """

    def get_commit( self ):
        """ Returns commit-string.
            Called by views.version() """
        original_directory = os.getcwd()
        log.debug( 'BASE_DIR, ```%s```' % settings.BASE_DIR )
        git_dir = settings.BASE_DIR
        log.debug( 'git_dir, ```%s```' % git_dir )
        os.chdir( git_dir )
        output_utf8 = subprocess.check_output( ['git', 'log'], stderr=subprocess.STDOUT )
        output = output_utf8.decode( 'utf-8' )
        os.chdir( original_directory )
        lines = output.split( '\n' )
        commit = lines[0]
        return commit


    def get_branch( self ):
        """ Returns branch.
            Called by views.version() """
        original_directory = os.getcwd()
        git_dir = settings.BASE_DIR
        os.chdir( git_dir )
        output_utf8 = subprocess.check_output( ['git', 'branch'], stderr=subprocess.STDOUT )
        output = output_utf8.decode( 'utf-8' )
        os.chdir( original_directory )
        lines = output.split( '\n' )
        branch = 'init'
        for line in lines:
            if line[0:1] == '*':
                branch = line[2:]
                break
        return branch

    def make_context( self, request, rq_now, info_txt, taken ):
        """ Builds and returns context.
            Called by views.info() """
        cntxt = {
            'request': {
                'url': '%s://%s%s' % ( request.scheme,
                    request.META.get( 'HTTP_HOST', '127.0.0.1' ),  # HTTP_HOST doesn't exist for client-tests
                    request.META.get('REQUEST_URI', request.META['PATH_INFO'])
                    ),
                'timestamp': str( rq_now )
            },
            'response': {
                'documentation': settings_app.DOCUMENTATION_URL,
                'version': info_txt,
                'elapsed_time': str( taken )
            }
        }
        return cntxt

    ## end Versioner()
