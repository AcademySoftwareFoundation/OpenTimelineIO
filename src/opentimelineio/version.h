// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#define OPENTIMELINEIO_VERSION_MAJOR 0
#define OPENTIMELINEIO_VERSION_MINOR 19
#define OPENTIMELINEIO_VERSION_PATCH 0
#define OPENTIMELINEIO_VERSION v0_19_0
#define OPENTIMELINEIO_VERSION_NS v0_19

#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentime/timeTransform.h"
#include "opentime/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {
using opentime::RationalTime;
using opentime::TimeRange;
using opentime::TimeTransform;
}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS

/// @brief Convenience macro for the full namespace of OpenTimelineIO API.
///
/// This can be used in place of the full namespace, e.g.:
/// <code>
///     OTIO_NS::Track* track = new OTIO_NS::Track;
/// </code>
///
#define OTIO_NS opentimelineio::OPENTIMELINEIO_VERSION_NS
