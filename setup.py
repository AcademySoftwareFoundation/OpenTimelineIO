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

import sys

from setuptools import setup


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

setup(
    name='OpenTimelineIO',
    version='0.8.dev',
    description='Editorial interchange format and API',
    author='Pixar Animation Studios',
    author_email='opentimelineio@pixar.com',
    url='http://opentimeline.io',

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
    ]
)
