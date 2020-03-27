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
from setuptools.command.install import install
from distutils.sysconfig import get_python_lib
from distutils.version import LooseVersion
import distutils


class _Ctx(object):
    pass


_ctx = _Ctx()
_ctx.cxx_install_root = None
_ctx.cxx_coverage = False
_ctx.build_temp_dir = None
_ctx.installed = False
_ctx.ext_dir = None
_ctx.source_dir = os.path.abspath(os.path.dirname(__file__))
_ctx.install_usersite = ''
_ctx.debug = False


def possibly_install(rerun_cmake):
    if (
            not _ctx.installed
            and _ctx.build_temp_dir
            and _ctx.cxx_install_root is not None
    ):
        installed = True # noqa

        if rerun_cmake:
            cmake_args, env = compute_cmake_args()
            subprocess.check_call(
                ['cmake', _ctx.source_dir] + cmake_args,
                cwd=_ctx.build_temp_dir,
                env=env
            )

        if platform.system() == "Windows":
            cmake_args, env = compute_cmake_args()
            subprocess.check_call(
                ['cmake', '--build', '.', '--target', 'install', '--config', 'Release'],
                cwd=_ctx.build_temp_dir,
                env=env
            )

        else:
            subprocess.check_call(
                ['make', 'install', '-j4'],
                cwd=_ctx.build_temp_dir
            )


def compute_cmake_args():
    cmake_args = [
        '-DPYTHON_EXECUTABLE=' + sys.executable,
        '-DOTIO_PYTHON_INSTALL:BOOL=ON'
    ]

    if _ctx.cxx_install_root is not None and _ctx.ext_dir:
        cmake_args.append('-DOTIO_PYTHON_OTIO_DIR=' + _ctx.ext_dir)
        if _ctx.cxx_install_root:
            cmake_args += ['-DCMAKE_INSTALL_PREFIX=' + _ctx.cxx_install_root]

        else:
            if "--user" in sys.argv:
                cxxLibDir = os.path.abspath(
                    os.path.join(_ctx.install_usersite, "opentimelineio", "cxx-libs")
                )
            else:
                cxxLibDir = os.path.abspath(
                    os.path.join(get_python_lib(), "opentimelineio", "cxx-libs")
                )
            cmake_args += ['-DCMAKE_INSTALL_PREFIX=' + cxxLibDir,
                           '-DOTIO_CXX_NOINSTALL:BOOL=ON']

    cfg = 'Debug' if _ctx.debug else 'Release'

    if platform.system() == "Windows":
        if sys.maxsize > 2**32:
            cmake_args += ['-A', 'x64']
    else:
        cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]

    if _ctx.cxx_coverage:
        cmake_args += ['-DCXX_COVERAGE=1'] + cmake_args

    env = os.environ.copy()

    return cmake_args, env


def _debugInstance(x):
    for a in sorted(dir(x)):
        print("%s:     %s" % (a, getattr(x, a)))


class Install(install):
    user_options = install.user_options + [
        (
            'cxx-install-root=',
            None,
            'Root directory for installing C++ headers/libraries'
            ' (required if you want to develop in C++)'
        ),
    ]

    def initialize_options(self):
        self.cxx_install_root = ""
        install.initialize_options(self)

    def run(self):
        _ctx.cxx_install_root = self.cxx_install_root
        _ctx.install_usersite = self.install_usersite
        possibly_install(rerun_cmake=True)
        install.run(self)


class CMakeExtension(Extension):
    def __init__(self, name):
        Extension.__init__(self, name, sources=[])


class CMakeBuild(setuptools.command.build_ext.build_ext):
    user_options = setuptools.command.build_ext.build_ext.user_options + [
        (
            'cxx-coverage',
            None,
            'Enable code coverage for C++ code.  NOTE: you will likely want to'
            ' also set the build_tmp directory to something that does not get '
            'cleaned up.',
        )
    ]

    def initialize_options(self):
        self.cxx_coverage = False
        setuptools.command.build_ext.build_ext.initialize_options(self)

    def run(self):
        # because tox passes all commandline arguments to _all_ things being
        # installed by setup.py (including dependencies), environment variables
        _ctx.cxx_coverage = (
            self.cxx_coverage is not False
            or bool(os.environ.get("OTIO_CXX_COVERAGE_BUILD"))
        )
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: "
                + ", ".join(e.name for e in self.extensions)
            )

        if platform.system() == "Windows":
            cmake_version = LooseVersion(
                re.search(r'version\s*([\d.]+)', out.decode()).group(1)
            )
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        self.build()

    def build(self):
        _ctx.ext_dir = os.path.join(os.path.abspath(self.build_lib), "opentimelineio")

        _ctx.build_temp_dir = (
            os.environ.get("OTIO_CXX_BUILD_TMP_DIR")
            or os.path.abspath(self.build_temp)
        )
        _ctx.debug = self.debug or bool(os.environ.get("OTIO_CXX_DEBUG_BUILD"))

        # from cmake_example PR #16
        if not _ctx.ext_dir.endswith(os.path.sep):
            _ctx.ext_dir += os.path.sep

        cmake_args, env = compute_cmake_args()

        cfg = 'Debug' if _ctx.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            build_args += ['--', '/m']
        else:
            build_args += ['--', '-j2']

        if not os.path.exists(_ctx.build_temp_dir):
            os.makedirs(_ctx.build_temp_dir)

        subprocess.check_call(
            ['cmake', _ctx.source_dir] + cmake_args,
            cwd=_ctx.build_temp_dir,
            env=env
        )
        subprocess.check_call(
            ['cmake', '--build', '.'] + build_args,
            cwd=_ctx.build_temp_dir
        )

        possibly_install(rerun_cmake=False)


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
    "version": "0.12.1",
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
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
        ]
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

    install_requires=(
        [
            'pyaaf2==1.2.0',
        ]
    ),
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
            'flake8>=3.5',
            'coverage>=4.5',
            'tox>=3.0',
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

    # Use the code that wires the PROJECT_METADATA into the __init__ files.
    cmdclass={
        'build_py': AddMetadataToInits,
        'build_ext': CMakeBuild,
        'install': Install,
    },

    # expand the project metadata dictionary to fill in those values
    **PROJECT_METADATA
)
