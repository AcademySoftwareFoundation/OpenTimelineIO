# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import sys
import tempfile
import pytest

import opentimelineio as otio


class TestCoreFunctions:
    def test_deserialize_json_from_file_errors(self):
        """Verify that the bindings return the correct errors based on the errno"""
        if sys.version_info[0] < 3:
            excType = OSError
        else:
            excType = FileNotFoundError  # noqa: F821

        with pytest.raises(excType) as exc:
            otio.core.deserialize_json_from_file("non-existent-file-here")
            assert isinstance(exc.exception, excType)

    @pytest.mark.skipif(
        not sys.platform.startswith("win"), reason="requires non Windows sytem"
    )  # noqa
    def test_serialize_json_to_file_errors_non_windows(self):
        """Verify that the bindings return the correct errors based on the errno"""
        if sys.version_info[0] < 3:
            excType = OSError
        else:
            excType = IsADirectoryError  # noqa: F821

        with pytest.raises(excType) as exc:
            otio.core.serialize_json_to_file({}, tempfile.mkdtemp())
        assert isinstance(exc.exception, excType)

    @pytest.mark.skipif(not sys.platform.startswith("win"), reason="requires Windows")
    def test_serialize_json_to_file_errors_windows(self):
        """Verify that the bindings return the correct errors based on the errno"""
        if sys.version_info[0] < 3:
            excType = OSError
        else:
            excType = PermissionError  # noqa: F821

        with pytest.raises(excType) as exc:
            otio.core.serialize_json_to_file({}, tempfile.mkdtemp())
        assert isinstance(exc.exception, excType)


def myTestCoreFunctions():
    return


# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project
