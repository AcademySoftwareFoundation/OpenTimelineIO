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
import setuptools.command.build_py
import sys
import unittest
from glob import glob
from distutils.util import convert_path
import tempfile
import shutil


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
    "version": "0.8.0.dev1",
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

EXPORTED_MODULES = [
    "opentimelineio",
    "opentimelineio_contrib",
    "opentimelineview",
]


def _append_version_info_to_init_scripts(build_lib):
    """Stamp PROJECT_METADATA into __init__ files."""

    for module in EXPORTED_MODULES:
        target_file = os.path.join(LIB_PATH, module, "__init__.py")
        source_file = os.path.join(
            os.path.dirname(__file__),
            module, "__init__.py"
        )

        # get the base data from the original file
        with open(source_file, 'r') as fi:
            src_data = fi.read()

        # write that + the suffix to the target file
        print "stamped: ", target_file
        with open(target_file, 'w') as fo:
            fo.write(src_data)
            fo.write(METADATA_TEMPLATE.format(**PROJECT_METADATA))
        print("success")


class AddMetadataToInits(setuptools.command.build_py.build_py):
    """Stamps PROJECT_METADATA into __init__ files."""

    def get_data_files(self):
        """Generate list of '(package,src_dir,build_dir,filenames)' tuples"""
        data = []
        if not self.packages:
            return data
        for package in self.packages:
            # Locate package source directory
            src_dir = self.get_package_dir(package)

            # Compute package build directory
            build_dir = os.path.join(*([self.build_lib] + package.split('.')))

            # Length of path to strip from found files
            plen = 0
            if src_dir:
                plen = len(src_dir)+1

            # Strip directory from globbed filenames
            filenames = [
                f[plen:] for f in self.find_data_files(package, src_dir)
            ]
            data.append((package, src_dir, build_dir, filenames))
        return data

    def find_data_files(self, package, src_dir):
        """Return filenames for package's data files in 'src_dir'"""
        globs = (self.package_data.get('', [])
                 + self.package_data.get(package, []))
        files = []
        for pattern in globs:
            # Each pattern has to be converted to a platform-specific path
            filelist = glob(os.path.join(src_dir, convert_path(pattern)))
            # Files that match more than one pattern are only added once
            files.extend([fn for fn in filelist if fn not in files
                and os.path.isfile(fn)])
        return files

    def run(self):
        # print "FOO:", self.get_data_files(), self.packages
        # print "package_dirs", [self.get_package_dir(p) for p in self.packages]
        # print "package_dirs", self.get_source_files()
        # print "BAR"
        import distutils.dist
        import distutils.command.build
        b = distutils.command.build.build(distutils.dist.Distribution())
        b.finalize_options()
        print("thing is: "+ b.build_lib)

        if not self.dry_run:
            _append_version_info_to_init_scripts(self.build_lib)


        setuptools.command.build_py.build_py.run(self)


def test_otio():
    """Discovers and runs tests"""
    try:
        # Clear the environment of a preset media linker
        del os.environ['OTIO_DEFAULT_MEDIA_LINKER']
    except KeyError:
        pass
    return unittest.TestLoader().discover('tests')


def _copy_to_var_tmp():
    temp_dir = tempfile.mkdtemp()

    for module in EXPORTED_MODULES:
        full_path = os.path.join(temp_dir, module)

        shutil.copytree(module, full_path)

    print "copied to", full_path

    return temp_dir


LIB_PATH = _copy_to_var_tmp()


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
            'https://github.com/PixarAnimationStudios/OpenTimelineIO/wiki',
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
    entry_points={
        'console_scripts': [
            'otioview = bin.otioview:main',
            'otiocat = bin.otiocat:main',
            'otioconvert = bin.otioconvert:main',
        ],
    },
    extras_require={
        'dev': [
            'flake8==3.5',
            'coverage==4.5',
        ]
    },
    test_suite='setup.test_otio',

    # because we need to open() the adapters manifest, we aren't zip-safe
    zip_safe=False,

    # Use the code that wires the PROJECT_METADATA into the __init__ files.
    cmdclass={'build_py': AddMetadataToInits},

    # use the stuff in /var/tmp
    package_dir = {'':LIB_PATH},

    # expand the project metadata dictionary to fill in those values
    **PROJECT_METADATA
)
