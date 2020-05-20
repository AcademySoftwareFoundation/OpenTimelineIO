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
import sys
import ast
import socket
import zipfile
import tempfile
import unittest
import shutil
import shlex
import time
import imp
from subprocess import call, Popen, PIPE

import opentimelineio as otio

RV_OTIO_READER_NAME = 'Example OTIO Reader'
RV_OTIO_READER_VERSION = '1.0'

RV_ROOT_DIR = os.getenv('OTIO_RV_ROOT_DIR', '')
RV_BIN_DIR = os.path.join(RV_ROOT_DIR, 'bin')

RV_OTIO_READER_DIR = os.path.join(
    '..',
    'rv',
    'example_otio_reader'
)

# Import rvNetwork with imp to compensate for older RV's missing __init__.py
RV_NETWORK_MODULE = os.path.join(
    RV_ROOT_DIR,
    'src',
    'python',
    'network',
    'rvNetwork.py'
)
rvNetwork = imp.load_source('rvNetwork', RV_NETWORK_MODULE)

# Generate sample data
sample_timeline = otio.schema.Timeline(
    'my_timeline',
    global_start_time=otio.opentime.RationalTime(1, 24)
)
track = otio.schema.Track('v1')
for clipnum in range(1, 4):
    clip_name = 'clip{n}'.format(n=clipnum)
    track.append(
        otio.schema.Clip(
            clip_name,
            media_reference=otio.schema.ExternalReference(
                target_url="{clip_name}.mov".format(clip_name=clip_name),
                available_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(1, 24),
                    otio.opentime.RationalTime(50, 24)
                )
            ),
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(11, 24),
                otio.opentime.RationalTime(30, 24)
            )
        )
    )
sample_timeline.tracks.append(track)


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

    def test_create_rvpkg(self):
        temp_dir = self.create_temp_dir()
        package_path = create_rvpkg(temp_dir)

        self.assertTrue(os.path.exists(package_path))
        self.assertTrue(os.path.getsize(package_path) > 0)

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_install_plugin(self):
        temp_dir = self.create_temp_dir()
        source_package_path = create_rvpkg(temp_dir)

        # Install package
        rc = install_package(source_package_path)

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
                   '-only {tmp_dir} -list'\
                   .format(
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
        source_package_path = create_rvpkg(temp_dir)
        install_package(source_package_path)

        env = os.environ.copy()
        env.update({'RV_SUPPORT_PATH': temp_dir})

        sample_file = tempfile.NamedTemporaryFile(
            'w',
            prefix='otio_data_',
            suffix='.otio',
            dir=temp_dir,
            delete=False
        )
        otio.adapters.write_to_file(sample_timeline, sample_file.name)
        run_cmd = '{root}/rv ' \
                  '-nc ' \
                  '-network ' \
                  '-networkHost localhost ' \
                  '-networkPort {port} ' \
                  '{sample_file}' \
                  .format(
                      root=RV_BIN_DIR,
                      port=9876,
                      sample_file=sample_file.name
                  )
        proc = Popen(shlex.split(run_cmd), env=env)

        # Connect with RV
        rvc = rvNetwork.RvCommunicator()

        try:
            attempts = 0
            while not rvc.connected:
                attempts += 1
                rvc.connect('localhost', 9876)

                if not rvc.connected:
                    time.sleep(.5)

                if attempts == 10:
                    raise socket.error(
                        "Unable to connect to RV!"
                    )

            # Check clips at positions
            clip1 = rv_media_name_at_frame(rvc, 1)
            self.assertEqual(clip1, 'clip1.mov')

            clip2 = rv_media_name_at_frame(rvc, 20)
            self.assertEqual(clip2, 'clip2.mov')

            clip3 = rv_media_name_at_frame(rvc, 40)
            self.assertEqual(clip3, 'clip3.mov')

            rvc.disconnect()

        finally:
            # Cleanup
            proc.terminate()
            shutil.rmtree(temp_dir)


def create_rvpkg(temp_dir):
    package_path = os.path.join(
        temp_dir,
        'example_otio_reader_plugin-{version}.rvpkg'
        .format(version=RV_OTIO_READER_VERSION)
    )
    with zipfile.ZipFile(package_path, 'w') as pkg:
        for item in os.listdir(RV_OTIO_READER_DIR):
            pkg.write(os.path.join(RV_OTIO_READER_DIR, item), item)

    return package_path


def install_package(source_package_path):
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


def rv_media_name_at_frame(rvc, frame):
    command = "rv.commands.sourcesAtFrame({0})".format(frame)
    source = rvc.sendEventAndReturn("remote-pyeval", command)
    source_list = ast.literal_eval(source)
    source_name = source_list[0]

    command = "rv.commands.sourceMedia('{0}')".format(source_name)
    media_string = rvc.sendEventAndReturn("remote-pyeval", command)
    media = ast.literal_eval(media_string)[0]

    return media


if __name__ == '__main__':
    unittest.main()
