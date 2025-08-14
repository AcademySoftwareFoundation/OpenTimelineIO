// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/track.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief Trim the track to the given range.
OPENTIMELINEIO_EXPORT Track* track_trimmed_to_range(
    Track*       in_track,
    TimeRange    trim_range,
    ErrorStatus* error_status = nullptr);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
