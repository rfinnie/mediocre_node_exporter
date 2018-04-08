#!/usr/bin/env python3

import subprocess
import os
import sys


VERSION = '0'

_scriptdir = os.path.dirname(os.path.realpath(__file__))

try:
    GIT_BRANCH = subprocess.check_output(
        ['git', '-C', _scriptdir, 'rev-parse', '--abbrev-ref', 'HEAD']
    ).decode('UTF-8').rstrip()
except subprocess.CalledProcessError:
    GIT_BRANCH = None

try:
    GIT_REVISION = subprocess.check_output(
        ['git', '-C', _scriptdir, 'show', '-s', '--format=%H']
    ).decode('UTF-8').rstrip()
except subprocess.CalledProcessError:
    GIT_REVISION = None

PYTHON_VERSION = sys.version.replace('\r', ' ').replace('\n', ' ')

if __name__ == '__main__':
    print('Version: {}'.format(VERSION))
    print('Git branch: {}'.format(GIT_BRANCH))
    print('Git revision: {}'.format(GIT_REVISION))
    print('Python version: {}'.format(PYTHON_VERSION))
