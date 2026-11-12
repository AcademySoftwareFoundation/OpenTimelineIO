# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""An editorial interchange format and library.

see: http://opentimeline.io

.. moduleauthor:: Contributors to the OpenTimelineIO project <otio-discussion@lists.aswf.io>
"""

# flake8: noqa

# in dependency hierarchy
from . import (
    opentime,
    exceptions,
    core,
    schema,
    schemadef,
    plugins,
    media_linker,
    adapters,
    hooks,
    algorithms,
    url_utils,
    versioning,
)

from ._version import __version__

__author__ = "Contributors to the OpenTimelineIO project"
__author_email__ = "otio-discussion@lists.aswf.io"
__license__ = "Apache 2.0 License"
