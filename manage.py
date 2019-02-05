#!/usr/bin/env python
import os
import sys
# first commit by Yang
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iip_smr_config.settings")
    print('Hi there')
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
