# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Unit tests for the rv reader plugin"""

# Please note that the test is geared towards linux install as I don't have
# a Windows or Mac available to me.

import os
import sys
import ast
import zipfile
import tempfile
import unittest
import shutil
import shlex
import time
import imp
import platform
from subprocess import call, Popen, PIPE

import opentimelineio as otio

RV_OTIO_READER_NAME = 'Example OTIO Reader'
RV_OTIO_READER_VERSION = '1.0'

RV_ROOT_DIR = os.getenv('OTIO_RV_ROOT_DIR', '')
RV_BIN_DIR = os.path.join(
    RV_ROOT_DIR,
    'MacOS' if platform.system() == 'Darwin' else 'bin'
)

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
bounds = [
    otio.schema.Box2d(
        otio.schema.V2d(0.0, 0.0),
        otio.schema.V2d(16.0, 9.0)
    ),  # sets viewing area
    otio.schema.Box2d(
        otio.schema.V2d(8.0, 0),
        otio.schema.V2d(24.0, 9.0)
    ),  # shifted right by half the viewing area
    otio.schema.Box2d(
        otio.schema.V2d(0.0, 0.0),
        otio.schema.V2d(8.0, 4.5)
    )  # scale to 1/4 of viewing area (lower left)
]

for clipnum, box in zip(range(1, 4), bounds):
    clip_name = f'clip{clipnum}'
    track.append(
        otio.schema.Clip(
            clip_name,
            media_reference=otio.schema.ExternalReference(
                target_url=f"{clip_name}.mov",
                available_range=otio.opentime.TimeRange(
                    otio.opentime.RationalTime(1, 24),
                    otio.opentime.RationalTime(50, 24)
                ),
                available_image_bounds=box
            ),
            source_range=otio.opentime.TimeRange(
                otio.opentime.RationalTime(11, 24),
                otio.opentime.RationalTime(3, 24)
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
                pkg_path=os.path.realpath(installed_package_path)
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
        run_cmd = '{root}/{exe} ' \
                  '-nc ' \
                  '-network ' \
                  '-networkHost localhost ' \
                  '-networkPort {port} ' \
                  '{sample_file}' \
                  .format(
                      exe='RV' if platform.system() == 'Darwin' else 'rv',
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

                if attempts == 20:
                    raise OSError(
                        "Unable to connect to RV!"
                    )

            # some time can pass between the RV connection
            # and the complete startup of RV
            print("Waiting for RV startup to complete")
            time.sleep(10)

            # Check clips at positions
            clip1 = rv_media_name_at_frame(rvc, 1)
            self.assertEqual(clip1, 'clip1.mov')

            # note RV has a default res of 1280,720 when the media doesn't exist
            aspect_ratio = 1280.0 / 720.0

            clip1_scale, clip1_translate = rv_transform_at_frame(rvc, 1)
            self.assertEqual(clip1_scale, [1.0, 1.0])
            self.assertEqual(clip1_translate, [0.0, 0.0])

            clip2 = rv_media_name_at_frame(rvc, 4)
            self.assertEqual(clip2, 'clip2.mov')

            clip2_scale, clip2_translate = rv_transform_at_frame(rvc, 4)
            self.assertEqual(clip2_scale, [1.0, 1.0])

            self.assertAlmostEqual(clip2_translate[0], 0.5 * aspect_ratio)
            self.assertEqual(clip2_translate[1], 0)

            clip3 = rv_media_name_at_frame(rvc, 7)
            self.assertEqual(clip3, 'clip3.mov')

            clip3_scale, clip3_translate = rv_transform_at_frame(rvc, 7)
            self.assertEqual(clip3_scale, [0.5, 0.5])

            self.assertAlmostEqual(clip3_translate[0], -0.25 * aspect_ratio)
            self.assertEqual(clip3_translate[1], -0.25)

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


def _exec_command(rvc, command, literal=True):
    response = rvc.sendEventAndReturn("remote-pyeval", command)
    return ast.literal_eval(response) if literal else response


def _source_at_frame(rvc, frame):
    return _exec_command(
        rvc,
        f"rv.commands.sourcesAtFrame({frame})"
    )[0]


def rv_media_name_at_frame(rvc, frame):
    source_name = _source_at_frame(rvc, frame)
    return _exec_command(
        rvc,
        f"rv.commands.sourceMedia('{source_name}')"
    )[0]


def rv_transform_at_frame(rvc, frame):
    source = _source_at_frame(rvc, frame)

    source_group = _exec_command(
        rvc,
        f"""rv.commands.nodeGroup('{source}')""",
        literal=False
    )

    transform = _exec_command(
        rvc,
        """rv.extra_commands.nodesInGroupOfType(
            '{}', 'RVTransform2D')""".format(source_group)
    )[0]

    scale = _exec_command(
        rvc,
        """rv.commands.getFloatProperty(
            '{}.transform.scale')""".format(transform)
    )

    translate = _exec_command(
        rvc,
        """rv.commands.getFloatProperty(
            '{}.transform.translate')""".format(transform)
    )

    return scale, translate


if __name__ == '__main__':
    unittest.main()
