# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Convert a string to a media reference policy."""

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
