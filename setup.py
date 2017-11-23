#!/usr/bin/env python3

import sys
from setuptools import setup

assert(sys.version_info > (3, 4))


setup(
    name='mediocre_node_exporter',
    description='A minimal node_exporter reimplementation',
    license='GPLv2+',
    platforms=['Unix'],
    author='Ryan Finnie',
    author_email='ryan@finnie.org',
    url='https://github.com/rfinnie/mediocre_node_exporter',
    download_url='https://github.com/rfinnie/mediocre_node_exporter',
    packages=[
        'm_n_e',
        'm_n_e.collectors',
    ],
    entry_points={
        'console_scripts': [
            'mediocre_node_exporter = m_n_e.cli:main',
        ],
    },
)
