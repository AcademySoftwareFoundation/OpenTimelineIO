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
