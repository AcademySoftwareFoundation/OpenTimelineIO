#! /usr/bin/env python

"""Setup.py for installing OpenTimelineIO

For more information:
- see README.md
- http://opentimeline.io
"""

import os
import re
import sys
import platform
import subprocess
import unittest
import pip

from setuptools import (
    setup,
    Extension,
    find_packages,
)

import setuptools.command.build_ext
import setuptools.command.build_py
from distutils.version import LooseVersion
import distutils

SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))


INSTALL_REQUIRES = [
    'pyaaf2~=1.4.0',
]
# python2 dependencies
if sys.version_info[0] < 3:
    INSTALL_REQUIRES.extend(
        [
            "backports.tempfile",
            'future',  # enables the builtins module in the XGES adapter
            "pathlib2"  # used in the otioz adapter to conform to unix paths
        ]
    )


def cmake_version_check():
    if platform.system() == "Windows":
        required_minimum_version = '3.17.0'
    else:
        required_minimum_version = '3.12.0'

    try:
        out = subprocess.check_output(['cmake', '--version'])
        cmake_version = LooseVersion(
            re.search(r'version\s*([\d.]+)', out.decode()).group(1)
        )
        if cmake_version < required_minimum_version:
            raise RuntimeError("CMake >= " + required_minimum_version +
                               " is required to build OpenTimelineIO's runtime"
                               " components")
    except OSError:
        if platform.system() == "Windows":
            raise RuntimeError("CMake >= 3.17.0 is required")
        raise RuntimeError("CMake >= 3.12.0 is required")


def _debugInstance(x):
    for a in sorted(dir(x)):
        print("%s:     %s" % (a, getattr(x, a)))


class CMakeExtension(Extension):
    def __init__(self, name):
        Extension.__init__(self, name, sources=[])


class OTIO_build_ext(setuptools.command.build_ext.build_ext):
    """
    def initialize_options(self):
        super(setuptools.command.build_ext.build_ext, self).initialize_options()
    """

    def run(self):
        # This works around the fact that we build _opentime and _otio
        # extensions as a one-shot cmake invocation. Usually we'd build each
        # separately using build_extension.
        self.build()

    def build(self):
        self.build_temp_dir = (
            os.environ.get("OTIO_CXX_BUILD_TMP_DIR")
            or os.path.abspath(self.build_temp)
        )

        if not os.path.exists(self.build_temp_dir):
            os.makedirs(self.build_temp_dir)

        debug = (self.debug or bool(os.environ.get("OTIO_CXX_DEBUG_BUILD")))
        self.build_config = ('Debug' if debug else 'Release')

        self.cmake_generate()
        self.cmake_install()

    def cmake_generate(self):
        # Determine the target directory for the built library
        install_dir = os.path.abspath(self.build_lib)
        if not install_dir.endswith(os.path.sep):
            install_dir += os.path.sep

        cmake_args = [
            '-DPYTHON_EXECUTABLE=' + sys.executable,
            '-DOTIO_PYTHON_INSTALL:BOOL=ON',
            '-DOTIO_CXX_INSTALL:BOOL=ON',
            '-DCMAKE_BUILD_TYPE=' + self.build_config,
            '-DPYBIND11_FINDPYTHON=ON',  # Smart tool to find python's libs
        ]  # https://pybind11.readthedocs.io/en/latest/compiling.html#findpython-mode

        # install the C++ into the opentimelineio/cxx-sdk directory under the
        # python installation
        cmake_install_prefix = os.path.join(
            install_dir,
            "opentimelineio",
            "cxx-sdk"
        )

        cmake_args += [
            '-DOTIO_PYTHON_INSTALL_DIR=' + install_dir,
            '-DCMAKE_INSTALL_PREFIX=' + cmake_install_prefix,
        ]

        if platform.system() == "Windows":
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']

        cxx_coverage = bool(os.environ.get("OTIO_CXX_COVERAGE_BUILD"))
        if cxx_coverage and not os.environ.get("OTIO_CXX_BUILD_TMP_DIR"):
            raise RuntimeError(
                "C++ code coverage requires that both OTIO_CXX_COVERAGE_BUILD=ON "
                "and OTIO_CXX_BUILD_TMP_DIR are specified as environment "
                "variables, otherwise coverage cannot be generated."
            )

        if cxx_coverage:
            cmake_args += ['-DOTIO_CXX_COVERAGE=1']

        cmake_args = ['cmake', SOURCE_DIR] + cmake_args
        subprocess.check_call(
            cmake_args,
            cwd=self.build_temp_dir,
            env=os.environ.copy()
        )

    def cmake_install(self):
        if platform.system() == "Windows":
            multi_proc = '/m'
        else:
            multi_proc = '-j2'

        subprocess.check_call(
            ['cmake', '--build', '.',
                '--target', 'install',
                '--config', self.build_config,
                '--', multi_proc],
            cwd=self.build_temp_dir,
            env=os.environ.copy()
        )


# Make sure the environment contains an up to date enough version of pip.
PIP_VERSION = pip.__version__
REQUIRED_PIP_VERSION = "6.0.0"
if (
        distutils.version.LooseVersion(PIP_VERSION)
        <= distutils.version.LooseVersion(REQUIRED_PIP_VERSION)
):
    sys.stderr.write(
        "Your pip version is: '{}', OpenTimelineIO requires at least "
        "version '{}'.  Please update pip by running:\n"
        "pip install -U pip\n".format(
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

REQUIRED_SETUPTOOLS_VERSION = '20.5.0'
if (
    distutils.version.LooseVersion(SETUPTOOLS_VERSION)
    <= distutils.version.LooseVersion(REQUIRED_SETUPTOOLS_VERSION)
):
    sys.stderr.write(
        "Your setuptools version is: '{}', OpenTimelineIO requires at least "
        "version '{}'.  Please update setuptools by running:\n"
        "pip install -U setuptools\n".format(
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
    "version": "0.14.0.dev1",
    "author": 'Contributors to the OpenTimelineIO project',
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

    for module, parentdir in [
            ("opentimelineio", "src/py-opentimelineio"),
            ("opentimelineio_contrib", "contrib"),
            ("opentimelineview", "src")
    ]:
        target_file = os.path.join(build_lib, module, "__init__.py")
        source_file = os.path.join(
            os.path.dirname(__file__),
            parentdir,
            module,
            "__init__.py"
        )

        # get the base data from the original file
        with open(source_file, 'r') as fi:
            src_data = fi.read()

        # write that + the suffix to the target file
        with open(target_file, 'w') as fo:
            fo.write(src_data)
            fo.write(METADATA_TEMPLATE.format(**PROJECT_METADATA))


class OTIO_build_py(setuptools.command.build_py.build_py):
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


cmake_version_check()


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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        'Natural Language :: English',
    ],

    keywords='film tv editing editorial edit non-linear edl time',

    platforms='any',

    package_data={
        'opentimelineio': [
            'adapters/builtin_adapters.plugin_manifest.json',
        ],
        'opentimelineio_contrib': [
            'adapters/contrib_adapters.plugin_manifest.json',
        ],
    },

    include_package_data=True,
    packages=(
        find_packages(where="src/py-opentimelineio") +
        find_packages(where="src") +
        find_packages(where="contrib")
    ),
    ext_modules=[
        CMakeExtension('_opentimelineio'),
        CMakeExtension('_opentime'),
    ],

    package_dir={
        'opentimelineio_contrib': 'contrib/opentimelineio_contrib',
        'opentimelineio': 'src/py-opentimelineio/opentimelineio',
        'opentimelineview': 'src/opentimelineview',
    },

    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': [
            'otioview = opentimelineview.console:main',
            'otiocat = opentimelineio.console.otiocat:main',
            'otioconvert = opentimelineio.console.otioconvert:main',
            'otiostat = opentimelineio.console.otiostat:main',
            'otiopluginfo = opentimelineio.console.otiopluginfo:main',
            (
                'otioautogen_serialized_schema_docs = '
                'opentimelineio.console.autogen_serialized_datamodel:main',
            )
        ],
    },
    extras_require={
        'dev': [
            'check-manifest',
            'flake8>=3.5',
            'coverage>=4.5',
            'urllib3>=1.24.3'
        ],
        'view': [
            'PySide2~=5.11'
        ]
    },

    test_suite='setup.test_otio',

    tests_require=[
        'mock;python_version<"3.3"',
    ],

    # because we need to open() the adapters manifest, we aren't zip-safe
    zip_safe=False,

    # The sequence of operations performed by setup.py is:
    #   OTIO_install::initialize
    #   OTIO_install::run
    #   OTIO_build_py::run
    #   the OpenTimelineIO egg is created
    #   OTIO_build_ext::initialize_options
    #   MANIFEST.in is read
    #   the lack of CHANGELOG.md is then reported.
    #   OTIO_build_ext::run is called
    #   OTIO_build_ext::build
    #   site-packages/opentimelineio* is populated with all scripts and extensions.
    #   pyc's are created for every python script.
    #   The egg is moved into site-packages,
    #   wrapper scripts for all the otiotools are created in a bin directory at the
    #   installation root.

    cmdclass={
        'build_py': OTIO_build_py,
        'build_ext': OTIO_build_ext,
    },

    # expand the project metadata dictionary to fill in those values
    **PROJECT_METADATA
)
