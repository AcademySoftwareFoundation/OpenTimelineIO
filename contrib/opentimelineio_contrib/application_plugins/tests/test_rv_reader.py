#
# Copyright Contributors to the OpenTimelineIO project
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

"""Unit tests for the rv reader plugin"""

# Please note that the test is geared towards linux install as I don't have
# a Windows or Mac available to me.

import os
import zipfile
import tempfile
import unittest
import shutil
import sys
import shlex
from subprocess import call, Popen, PIPE

import opentimelineio as otio
print otio.__file__
RV_OTIO_READER_NAME = 'Example OTIO Reader'
RV_OTIO_READER_VERSION = '1.0'

OTIO_SAMPLE_DATA_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "adapters",
    "tests",
    "sample_data"
)
RV_ROOT_DIR = os.getenv('OTIO_RV_ROOT_DIR', '')
RV_BIN_DIR = os.path.join(RV_ROOT_DIR, 'bin')

RV_OTIO_READER_DIR = os.path.join(
    '..',
    'rv',
    'example_otio_reader'
)

@unittest.skipIf(
    "OTIO_RV_ROOT_DIR" not in os.environ,
    "OTIO_RV_ROOT_DIR not set."
)
@unittest.skipIf(
    (sys.version_info > (3, 0)),
    "RV OTIO reader plugin does not work in python 3."
)
class RVSessionAdapterReadTest(unittest.TestCase):
    def create_temp_dir(self):
        return tempfile.mkdtemp(prefix='rv_otio_reader')

    def create_rvpkg(self, temp_dir):
        package_path = os.path.join(
            temp_dir,
            'example_otio_reader_plugin-{version}.rvpkg'
            .format(version=RV_OTIO_READER_VERSION)
        )
        with zipfile.ZipFile(package_path, 'w') as pkg:
            for item in os.listdir(RV_OTIO_READER_DIR):
                pkg.write(os.path.join(RV_OTIO_READER_DIR, item), item)

        return package_path

    def install_package(self, source_package_path):
        install_cmd = '{root}/rvpkg -force ' \
                      '-install ' \
                      '-add {tmp_dir} ' \
                      '{pkg_file}'.format(
                          root=RV_BIN_DIR,
                          tmp_dir=os.path.dirname(source_package_path),
                          pkg_file=source_package_path
                      )
        rc = call(shlex.split(install_cmd))
        return rc

    def test_create_rvpkg(self):
        temp_dir = self.create_temp_dir()
        package_path = self.create_rvpkg(temp_dir)

        self.assertTrue(os.path.exists(package_path))
        self.assertTrue(os.path.getsize(package_path) > 0)

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_install_plugin(self):
        temp_dir = self.create_temp_dir()
        source_package_path = self.create_rvpkg(temp_dir)

        # Install package
        rc = self.install_package(source_package_path)

        # Check if install succeeded
        installed_package_path = os.path.join(
            temp_dir,
            'Packages',
            os.path.basename(source_package_path)
        )

        self.assertTrue(rc == 0)
        self.assertTrue(len(os.listdir(temp_dir)) > 1)
        self.assertTrue(os.path.exists(installed_package_path))

        # Make sure package is available in RV
        list_cmd = '{root}/rvpkg ' \
                   '-only {tmp_dir} -list'.format(
                        root=RV_BIN_DIR,
                        tmp_dir=temp_dir
                    )

        proc = Popen(shlex.split(list_cmd), stdout=PIPE)
        stdout, _ = proc.communicate()

        desired_result = \
            'I L - {version} "{package_name}" {pkg_path}'.format(
                version=RV_OTIO_READER_VERSION,
                package_name=RV_OTIO_READER_NAME,
                pkg_path=installed_package_path
            )

        self.assertIn(desired_result, stdout.split('\n'))

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_read_otio_file(self):
        # Install package
        temp_dir = self.create_temp_dir()
        source_package_path = self.create_rvpkg(temp_dir)
        self.install_package(source_package_path)

        env = os.environ.copy()
        env.update({'RV_SUPPORT_PATH': temp_dir})

        sample_file = os.path.join(
            OTIO_SAMPLE_DATA_DIR, 'rv_metadata.otio'
        )
        run_cmd = '{root}/rv ' \
                  '{sample_file}'.format(
                      root=RV_BIN_DIR,
                      sample_file=sample_file
                    )
        rc = call(shlex.split(run_cmd), env=env)
        self.assertTrue(rc == 0)

        # Cleanup
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()
