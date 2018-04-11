#!/usr/bin/env python
#
# Copyright 2017 Pixar Animation Studios
#
# Licensed under the Apache License, Version 2.0 (the "Apache License")
# with the following modification; you may not use this file except in
# compliance with the Apache License and the following modification to it:
# Section 6. Trademarks. is deleted and replaced with:
#
# 6. Trademarks. This License does not grant permission to use the trade
#    names, trademarks, service marks, or product names of the Licensor
#    and its affiliates, except as required to comply with Section 4(c) of
#    the License and to reproduce the content of the NOTICE file.
#
# You may obtain a copy of the Apache License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Apache License with the above modification is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the Apache License for the specific
# language governing permissions and limitations under the Apache License.
#

""" Configuration file for the OpenTimelineIO Python Package.  """

import os
from setuptools import setup
import sys
import unittest


# check the python version first
if (
    sys.version_info[0] < 2 or
    (sys.version_info[0] == 2 and sys.version_info[1] < 7)
):
    sys.exit(
        'OpenTimelineIO requires python2.7 or greater, detected version:'
        ' {}.{}'.format(
            sys.version_info[0],
            sys.version_info[1]
        )
    )


def test_otio():
    """Discovers and runs tests"""
    try:
        # Clear the environment of a preset media linker
        del os.environ['OTIO_DEFAULT_MEDIA_LINKER']
    except KeyError:
        pass
    return unittest.TestLoader().discover('tests')


# copied from first paragraph of README.md
LONG_DESCRIPTION = """OpenTimelineIO is an interchange format and API for
editorial cut information. OTIO is not a container format for media, rather it
contains information about the order and length of cuts and references to
external media.

OTIO includes both a file format and an API for manipulating that format. It
also includes a plugin architecture for writing adapters to convert from/to
existing editorial timeline formats. It also implements a dependency- less
library for dealing strictly with time, opentime.

You can provide adapters for your video editing tool or pipeline as needed.
Each adapter allows for import/export between that proprietary tool and the
OpenTimelineIO format."""

setup(
    name='OpenTimelineIO',
    version='0.7.1',
    description='Editorial interchange format and API',
    long_description=LONG_DESCRIPTION,
    author='Pixar Animation Studios',
    author_email='opentimelineio@pixar.com',
    url='http://opentimeline.io/',
    project_urls={
        'Source':
            'https://github.com/PixarAnimationStudios/OpenTimelineIO',
        'Documentation':
            'https://github.com/PixarAnimationStudios/OpenTimelineIO/wiki',
        'Issues':
            'https://github.com/PixarAnimationStudios/OpenTimelineIO/issues',
    },    license='Modified Apache 2.0 License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Multimedia :: Video :: Non-Linear Editor',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
        'Natural Language :: English',
    ],

    keywords='film tv editing editorial edit non-linear edl time',

    platforms='any',

    packages=[
        'opentimelineio',
        'opentimelineio.adapters',
        'opentimelineio.algorithms',
        'opentimelineio.core',
        'opentimelineio.schema',
        'opentimelineio.plugins',
        'opentimelineio_contrib',
        'opentimelineio_contrib.adapters',
        'opentimelineview'
    ],

    package_data={
        'opentimelineio': [
            'adapters/builtin_adapters.plugin_manifest.json',
        ],
        'opentimelineio_contrib': [
            'adapters/contrib_adapters.plugin_manifest.json',
        ]
    },

    scripts=[
        'bin/otiocat.py',
        'bin/otioconvert.py',
        'bin/otioview.py'
    ],

    install_requires=[
        # PyAAF2 to go here eventually
    ],

    test_suite='setup.test_otio',

)
