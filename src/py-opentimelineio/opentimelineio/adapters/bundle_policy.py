# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Turns a media policy written as a string into the enumeration.

The bundle adapters take their arguments from whoever calls them, and from
the commandline that is always a string: `otioconvert -A
media_policy=all_missing` reaches the adapter as the text `all_missing`,
which is not a value the enumeration will accept.

Both spellings are understood: the names the enumeration uses, and the
names the adapters used before it, which is what documentation and scripts
written against those versions say.
"""

from .. import (
    _otio
)


_POLICIES = {
    "error_if_not_file": _otio.bundle.MediaReferencePolicy.error_if_not_file,
    "missing_if_not_file": _otio.bundle.MediaReferencePolicy.missing_if_not_file,
    "all_missing": _otio.bundle.MediaReferencePolicy.all_missing,
    # The names used before the policy became an enumeration.
    "errorifnotfile": _otio.bundle.MediaReferencePolicy.error_if_not_file,
    "missingifnotfile": _otio.bundle.MediaReferencePolicy.missing_if_not_file,
    "allmissing": _otio.bundle.MediaReferencePolicy.all_missing,
}


def media_reference_policy(value):
    """Return ``value`` as a MediaReferencePolicy.

    Anything that is not a string is returned unchanged, so a caller that
    already has a policy is unaffected.
    """

    if not isinstance(value, str):
        return value

    try:
        return _POLICIES[value.lower().replace("-", "_")]
    except KeyError:
        raise ValueError(
            "unknown media policy '{}', expected one of: {}".format(
                value,
                ", ".join(sorted(
                    n for n in _POLICIES if "_" in n
                ))
            )
        )
