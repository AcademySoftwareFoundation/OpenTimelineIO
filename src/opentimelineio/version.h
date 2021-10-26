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

/// Convenience macro for the full namespace of OpenTimelineIO API.
///
/// This can be used in place of the full namespace, e.g.:
///     OTIO_NS::Track* track = new OTIO_NS::Track;
///
#define OTIO_NS opentimelineio::OPENTIMELINEIO_VERSION
