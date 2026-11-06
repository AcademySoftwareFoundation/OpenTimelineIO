// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#define OPENTIMELINEIO_VERSION_MAJOR 0
#define OPENTIMELINEIO_VERSION_MINOR 19
#define OPENTIMELINEIO_VERSION_PATCH 0

// The version and namespace names are made from the numbers above, for
// example v0_19_0 and v0_19.
#define OPENTIMELINEIO_VERSION_JOIN3_(a, b, c) v##a##_##b##_##c
#define OPENTIMELINEIO_VERSION_JOIN3(a, b, c)                                  \
    OPENTIMELINEIO_VERSION_JOIN3_(a, b, c)
#define OPENTIMELINEIO_VERSION_JOIN2_(a, b) v##a##_##b
#define OPENTIMELINEIO_VERSION_JOIN2(a, b) OPENTIMELINEIO_VERSION_JOIN2_(a, b)
#define OPENTIMELINEIO_VERSION                                                 \
    OPENTIMELINEIO_VERSION_JOIN3(                                              \
        OPENTIMELINEIO_VERSION_MAJOR,                                          \
        OPENTIMELINEIO_VERSION_MINOR,                                          \
        OPENTIMELINEIO_VERSION_PATCH)
#define OPENTIMELINEIO_VERSION_NS                                              \
    OPENTIMELINEIO_VERSION_JOIN2(                                              \
        OPENTIMELINEIO_VERSION_MAJOR,                                          \
        OPENTIMELINEIO_VERSION_MINOR)

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
