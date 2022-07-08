#!/usr/bin/env python
#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

__doc__ = """The utility script checks to make sure that all of the source
files in the OpenTimelineIO project have the correct license header."""

import os
import sys

licenses = {
    ".py": """# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project
""",
    ".cpp": """// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project
""",
    ".c": """// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project
""",
    ".h": """// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project
""",
    ".swift": """// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project
""",
    ".mm": """// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project
"""
}

yes = 0
no = 0
total = 0

for root, dirs, files in os.walk("."):
    for filename in files:
        fullpath = os.path.join(root, filename)
        for ext, license in licenses.items():
            if filename.endswith(ext):
                total += 1
                try:
                    content = open(fullpath, 'r').read()
                except Exception as ex:
                    print("ERROR: Unable to read file: {}\n{}".format(
                        fullpath, ex))
                    # raise
                    continue
                if len(content) > 10 and license not in content:
                    print("MISSING: {}".format(fullpath))
                    no += 1
                else:
                    yes += 1

print("{} of {} files have the correct license.".format(yes, total))

if no != 0:
    print("ERROR: {} files do NOT have the correct license.".format(no))
    sys.exit(1)
