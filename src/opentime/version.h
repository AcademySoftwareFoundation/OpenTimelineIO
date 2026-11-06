// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#define OPENTIME_VERSION_MAJOR 0
#define OPENTIME_VERSION_MINOR 19
#define OPENTIME_VERSION_PATCH 0

// The version and namespace names are made from the numbers above, for
// example v0_19_0 and v0_19.
#define OPENTIME_VERSION_JOIN3_(a, b, c) v##a##_##b##_##c
#define OPENTIME_VERSION_JOIN3(a, b, c) OPENTIME_VERSION_JOIN3_(a, b, c)
#define OPENTIME_VERSION_JOIN2_(a, b) v##a##_##b
#define OPENTIME_VERSION_JOIN2(a, b) OPENTIME_VERSION_JOIN2_(a, b)
#define OPENTIME_VERSION                                                       \
    OPENTIME_VERSION_JOIN3(                                                    \
        OPENTIME_VERSION_MAJOR,                                                \
        OPENTIME_VERSION_MINOR,                                                \
        OPENTIME_VERSION_PATCH)
#define OPENTIME_VERSION_NS                                                    \
    OPENTIME_VERSION_JOIN2(OPENTIME_VERSION_MAJOR, OPENTIME_VERSION_MINOR)

namespace opentime {
namespace OPENTIME_VERSION_NS {
}

using namespace OPENTIME_VERSION_NS;
} // namespace opentime
