#!/usr/bin/env python

import sys

from distutils.core import setup


""" Configuration file for the OpenTimelineIO Python Package.  """

# check the python version first
if (
    sys.version_info[0] < 2 or
    (sys.version_info[0] == 2 and sys.version_info[1] < 6)
):
    sys.exit(
        'OpenTimelineIO requires python2.6 or greater, detected version:'
        ' {}.{}'.format(
            sys.version_info[0],
            sys.version_info[1]
        )
    )

setup(
    name='OpenTimelineIO',
    version='0.5.dev',
    description='Editorial interchange format and API',
    author='Pixar Animation Studios',
    author_email='opentimelineio@pixar.com',
    url='http://opentimeline.io',

    packages=[
        'opentimelineio',
        'opentimelineio.adapters',
        'opentimelineio.algorithms',
        'opentimelineio.core',
        'opentimelineio.plugins',
        'opentimelineio.schema',
        'opentimelineio.plugins',
        'opentimelineioViewWidget'
    ],

    package_data={
        'opentimelineio': ['adapters/builtin_adapters.plugin_manifest.json']
    },

    scripts=[
        'bin/otiocat.py',
        'bin/otioconvert.py',
        'bin/otioview.py'
    ]
)
