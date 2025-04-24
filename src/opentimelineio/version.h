// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#define OPENTIMELINEIO_VERSION v1_0

#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentime/timeTransform.h"
#include "opentime/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {
using opentime::RationalTime;
using opentime::TimeRange;
using opentime::TimeTransform;
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION

/// @brief Convenience macro for the full namespace of OpenTimelineIO API.
///
/// This can be used in place of the full namespace, e.g.:
/// <code>
///     OTIO_NS::Track* track = new OTIO_NS::Track;
/// </code>
///
#define OTIO_NS opentimelineio::OPENTIMELINEIO_VERSION
