#! /usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Setup.py for installing OpenTimelineIO

For more information:
- see README.md
- http://opentimeline.io
"""

import multiprocessing
import os
import shlex
import sys
import platform
import subprocess
import tempfile
import shutil

from setuptools import (
    setup,
    Extension,
    find_packages,
)

import setuptools.command.build_ext
import setuptools.command.build_py

SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))

PLAT_TO_CMAKE = {
    "win32": "Win32",
    "win-amd64": "x64",
}


def _debugInstance(x):
    for a in sorted(dir(x)):
        print("{}:     {}".format(a, getattr(x, a)))


def join_args(args):
    return ' '.join(map(shlex.quote, args))


class OTIO_build_ext(setuptools.command.build_ext.build_ext):
    """
    def initialize_options(self):
        super(setuptools.command.build_ext.build_ext, self).initialize_options()
    """

    built = False

    def run(self):
        self.announce('running OTIO build_ext', level=2)
        # Let the original build_ext class do its job.
        # This is rather important because build_ext.run takes care of a
        # couple of things, one of which is to copy the built files into
        # the source tree (in src/py-opentimelineio/opentimelineio)
        # when building in editable mode.
        super().run()

    def build_extension(self, _ext: Extension):
        # This works around the fact that we build _opentime and _otio
        # extensions as a one-shot cmake invocation. Setuptools calls
        # build_extension for each Extension registered in the setup function.
        if not self.built:
            self.build()
            self.built = True

    def build(self):
        self.build_temp_dir = (
            os.environ.get("OTIO_CXX_BUILD_TMP_DIR")
            or os.path.abspath(self.build_temp)
        )

        if not os.path.exists(self.build_temp_dir):
            os.makedirs(self.build_temp_dir)

        debug = (self.debug or bool(os.environ.get("OTIO_CXX_DEBUG_BUILD")))
        self.build_config = ('Debug' if debug else 'Release')

        self.cmake_preflight_check()
        self.cmake_generate()
        self.cmake_install()

    def is_windows(self):
        return platform.system() == "Windows"

    def is_mingw(self):
        return self.plat_name.startswith('mingw')

    def generate_cmake_arguments(self):
        # Use the provided build dir so setuptools will be able to locate and
        # either install to the correct location or package.
        install_dir = os.path.abspath(self.build_lib)
        if not install_dir.endswith(os.path.sep):
            install_dir += os.path.sep

        cmake_args = [
            # Python_EXECUTABLE is important as it tells CMake's FindPython
            # which Python executable to use. We absolutely want to use the
            # interpreter that was used to execute the setup.py.
            # See https://cmake.org/cmake/help/v3.20/module/FindPython.html#artifacts-specification # noqa: E501
            # Also, be careful, CMake is case sensitive ;)
            '-DPython_EXECUTABLE=' + sys.executable,
            '-DOTIO_PYTHON_INSTALL:BOOL=ON',
            '-DOTIO_CXX_INSTALL:BOOL=OFF',
            '-DOTIO_SHARED_LIBS:BOOL=OFF',
            '-DCMAKE_BUILD_TYPE=' + self.build_config,
            '-DOTIO_PYTHON_INSTALL_DIR=' + install_dir,
            # turn off the C++ tests during a Python build
            '-DBUILD_TESTING:BOOL=OFF',
            # Python modules wil be installed by setuptools.
            '-DOTIO_INSTALL_PYTHON_MODULES:BOOL=OFF',
        ]
        if self.is_windows():
            if self.is_mingw():
                cmake_args += ['-G Unix Makefiles']
            else:
                cmake_args += ["-A", PLAT_TO_CMAKE[self.plat_name]]

        cxx_coverage = bool(os.environ.get("OTIO_CXX_COVERAGE_BUILD"))
        if cxx_coverage and not os.environ.get("OTIO_CXX_BUILD_TMP_DIR"):
            raise RuntimeError(
                "C++ code coverage requires that both OTIO_CXX_COVERAGE_BUILD=ON "
                "and OTIO_CXX_BUILD_TMP_DIR are specified as environment "
                "variables, otherwise coverage cannot be generated."
            )

        if cxx_coverage:
            cmake_args += ['-DOTIO_CXX_COVERAGE=1']

        # allow external arguments to cmake via the CMAKE_ARGS env var
        cmake_args += [
            arg for arg in os.environ.get("CMAKE_ARGS", "").split(" ")
            if arg
        ]

        return cmake_args

    def cmake_preflight_check(self):
        """
        Verify that CMake is greater or equal to the required version
        We do this so that the error message is clear if the minimum version is not met.
        """
        self.announce('running cmake check', level=2)
        # We need to run cmake --check-system-vars because it will still generate
        # a CMakeCache.txt file.
        tmpdir = tempfile.mkdtemp(dir=self.build_temp_dir)

        args = ["--check-system-vars", SOURCE_DIR] + self.generate_cmake_arguments()

        proc = subprocess.Popen(
            ["cmake"] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=tmpdir,
            universal_newlines=True
        )

        _, stderr = proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(stderr.strip())

        shutil.rmtree(tmpdir)

    def cmake_generate(self):
        self.announce('running cmake generation', level=2)

        cmake_args = ['cmake', SOURCE_DIR] + self.generate_cmake_arguments()
        self.announce(join_args(cmake_args), level=2)

        subprocess.check_call(
            cmake_args,
            cwd=self.build_temp_dir,
            env=os.environ.copy()
        )

    def cmake_install(self):
        self.announce('running cmake build', level=2)
        if self.is_windows() and not self.is_mingw():
            multi_proc = '/m'
        else:
            multi_proc = f'-j{multiprocessing.cpu_count()}'

        cmake_args = [
            'cmake',
            '--build', '.',
            '--target', 'install',
            '--config', self.build_config,
            '--', multi_proc,
        ]

        self.announce(join_args(cmake_args), level=2)
        subprocess.check_call(
            cmake_args,
            cwd=self.build_temp_dir,
            env=os.environ.copy()
        )


# check the python version first
if (
    sys.version_info[0] < 3 or
    (sys.version_info[0] == 3 and sys.version_info[1] < 7)
):
    sys.exit(
        'OpenTimelineIO requires python3.7 or greater, detected version:'
        ' {}.{}'.format(
            sys.version_info[0],
            sys.version_info[1]
        )
    )


# Metadata that gets stamped into the __init__ files during the build phase.
PROJECT_METADATA = {
    "version": "0.16.0.dev1",
    "author": 'Contributors to the OpenTimelineIO project',
    "author_email": 'otio-discussion@lists.aswf.io',
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
        with open(source_file) as fi:
            src_data = fi.read()

        # write that + the suffix to the target file
        with open(target_file, 'w') as fo:
            fo.write(src_data)
            fo.write(METADATA_TEMPLATE.format(**PROJECT_METADATA))


class OTIO_build_py(setuptools.command.build_py.build_py):
    """Stamps PROJECT_METADATA into __init__ files."""

    def run(self):
        super().run()

        if not self.dry_run and not self.editable_mode:
            # Only run when not in dry-mode (a dry run should not have any side effect)
            # and in non-editable mode. We don't want to edit files when in editable
            # mode because that could lead to modifications to the source files.
            # Note that setuptools will set self.editable_mode to True
            # when "pip install -e ." is run.
            _append_version_info_to_init_scripts(self.build_lib)


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
    long_description_content_type='text/markdown',
    url='http://opentimeline.io',
    project_urls={
        'Source':
            'https://github.com/AcademySoftwareFoundation/OpenTimelineIO',
        'Documentation':
            'https://opentimelineio.readthedocs.io/',
        'Issues':
            'https://github.com/AcademySoftwareFoundation/OpenTimelineIO/issues',
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Multimedia :: Video :: Non-Linear Editor',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
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

    packages=(
        find_packages(where="src/py-opentimelineio") +  # opentimelineio
        find_packages(where="src") +  # opentimelineview
        find_packages(where="contrib", exclude=["opentimelineio_contrib.adapters.tests"])  # opentimelineio_contrib # noqa
    ),

    ext_modules=[
        # The full and correct module name is required here because
        # setuptools needs to resolve the name to find the built file
        # and copy it into the source tree. (Because yes, editable install
        # means that the install should point to the source tree, which
        # means the .sos need to also be there alongside the python files).
        Extension('opentimelineio._otio', sources=[]),
        Extension('opentimelineio._opentime', sources=[]),
    ],

    package_dir={
        'opentimelineio_contrib': 'contrib/opentimelineio_contrib',
        'opentimelineio': 'src/py-opentimelineio/opentimelineio',
        'opentimelineview': 'src/opentimelineview',
    },

    # Disallow 3.9.0 because of https://github.com/python/cpython/pull/22670
    python_requires='>=3.7, !=3.9.0',  # noqa: E501

    install_requires=[
        'pyaaf2>=1.4,<1.7',
    ],
    entry_points={
        'console_scripts': [
            'otiocat = opentimelineio.console.otiocat:main',
            'otioconvert = opentimelineio.console.otioconvert:main',
            'otiopluginfo = opentimelineio.console.otiopluginfo:main',
            'otiostat = opentimelineio.console.otiostat:main',
            'otiotool = opentimelineio.console.otiotool:main',
            'otioview = opentimelineview.console:main',
            (
                'otioautogen_serialized_schema_docs = '
                'opentimelineio.console.autogen_serialized_datamodel:main'
            ),
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
            'PySide2~=5.11; platform.machine=="x86_64"',
            'PySide6~=6.2; platform.machine=="aarch64"'
        ]
    },

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
