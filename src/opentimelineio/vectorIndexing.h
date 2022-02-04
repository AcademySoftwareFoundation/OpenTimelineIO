#pragma once

#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

template <typename V>
constexpr int
adjusted_vector_index(int index, V const& vec) noexcept
{
    return index < 0 ? int(vec.size()) + index : index;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
