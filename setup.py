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
import sys
import unittest
from setuptools import setup
import setuptools.command.build_py
import distutils.version
import pip


# Make sure the environment contains an up to date enough version of pip.
PIP_VERSION = pip.__version__
REQUIRED_PIP_VERSION = "6.0.0"
if (
        distutils.version.StrictVersion(PIP_VERSION)
        <= distutils.version.StrictVersion(REQUIRED_PIP_VERSION)
):
    print(
        "Your pip version is: '{}', OpenTimelineIO requires at least "
        "version '{}'.  Please update setuptools by running: "
        "pip install -U pip".format(
            PIP_VERSION,
            REQUIRED_PIP_VERSION,
        )
    )
    sys.exit(1)


# Make sure the environment contains an up to date enough version of setuptools.
try:
    import setuptools.version
    SETUPTOOLS_VERSION = setuptools.version.__version__
except ImportError:
    SETUPTOOLS_VERSION = setuptools.__version__

REQUIRED_SETUPTOOLS_VERSION = '38.3.0'
if (
    distutils.version.StrictVersion(SETUPTOOLS_VERSION)
    <= distutils.version.StrictVersion(REQUIRED_SETUPTOOLS_VERSION)
):
    print(
        "Your setuptools version is: '{}', OpenTimelineIO requires at least "
        "version '{}'.  Please update setuptools by running: "
        "pip install -U setuptools".format(
            SETUPTOOLS_VERSION,
            REQUIRED_SETUPTOOLS_VERSION,
        )
    )
    sys.exit(1)


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

# Metadata that gets stamped into the __init__ files during the build phase.
PROJECT_METADATA = {
    "version": "0.10.0.dev1",
    "author": 'Pixar Animation Studios',
    "author_email": 'opentimelineio@pixar.com',
    "license": 'Modified Apache 2.0 License',
}

METADATA_TEMPLATE = """
__version__ = "{version}"
__author__ = "{author}"
__author_email__ = "{author_email}"
__license__ = "{license}"
"""


def _append_version_info_to_init_scripts(build_lib):
    """Stamp PROJECT_METADATA into __init__ files."""

    for module in [
            "opentimelineio",
            "opentimelineio_contrib",
            "opentimelineview",
    ]:
        target_file = os.path.join(build_lib, module, "__init__.py")
        source_file = os.path.join(
            os.path.dirname(__file__),
            module, "__init__.py"
        )

        # get the base data from the original file
        with open(source_file, 'r') as fi:
            src_data = fi.read()

        # write that + the suffix to the target file
        with open(target_file, 'w') as fo:
            fo.write(src_data)
            fo.write(METADATA_TEMPLATE.format(**PROJECT_METADATA))


class AddMetadataToInits(setuptools.command.build_py.build_py):
    """Stamps PROJECT_METADATA into __init__ files."""

    def run(self):
        setuptools.command.build_py.build_py.run(self)

        if not self.dry_run:
            _append_version_info_to_init_scripts(self.build_lib)


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
    description='Editorial interchange format and API',
    long_description=LONG_DESCRIPTION,
    url='http://opentimeline.io',
    project_urls={
        'Source':
            'https://github.com/PixarAnimationStudios/OpenTimelineIO',
        'Documentation':
            'https://opentimelineio.readthedocs.io/',
        'Issues':
            'https://github.com/PixarAnimationStudios/OpenTimelineIO/issues',
    },

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
        'Programming Language :: Python :: 3.6',
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
        'opentimelineio.schemadef',
        'opentimelineio.plugins',
        'opentimelineio.console',
        'opentimelineio_contrib',
        'opentimelineio_contrib.adapters',
        'opentimelineview',
    ],

    package_data={
        'opentimelineio': [
            'adapters/builtin_adapters.plugin_manifest.json',
        ],
        'opentimelineio_contrib': [
            'adapters/contrib_adapters.plugin_manifest.json',
        ]
    },

    install_requires=[
        # PyAAF2 to go here eventually
    ],
    entry_points={
        'console_scripts': [
            'otioview = opentimelineview.console:main',
            'otiocat = opentimelineio.console.otiocat:main',
            'otioconvert = opentimelineio.console.otioconvert:main',
            'otiostat = opentimelineio.console.otiostat:main',
        ],
    },
    extras_require={
        'dev': [
            'flake8>=3.5',
            'coverage>=4.5',
            'tox>=3.0',
        ],
        'view': [
            'PySide2>=5.11'
        ]
    },

    test_suite='setup.test_otio',

    tests_require=[
            'mock;python_version<"3.3"',
    ],

    # because we need to open() the adapters manifest, we aren't zip-safe
    zip_safe=False,

    # Use the code that wires the PROJECT_METADATA into the __init__ files.
    cmdclass={'build_py': AddMetadataToInits},

    # expand the project metadata dictionary to fill in those values
    **PROJECT_METADATA
)
