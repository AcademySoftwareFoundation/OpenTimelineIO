# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

__doc__ = """ Read and write timelines bundled with their media, as .otioz
files or .otiod directories. """

from . import _otio

MediaReferencePolicy = _otio.bundle.MediaReferencePolicy
WriteOptions = _otio.bundle.WriteOptions
ReadOptions = _otio.bundle.ReadOptions
file_from_url = _otio.bundle.file_from_url
dry_run = _otio.bundle.dry_run
write_otioz = _otio.bundle.write_otioz
read_otioz = _otio.bundle.read_otioz
write_otiod = _otio.bundle.write_otiod
read_otiod = _otio.bundle.read_otiod
