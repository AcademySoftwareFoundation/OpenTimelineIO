// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief Return the adjusted vector index.
template <typename V>
constexpr int
adjusted_vector_index(int index, V const& vec) noexcept
{
    return index < 0 ? int(vec.size()) + index : index;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
