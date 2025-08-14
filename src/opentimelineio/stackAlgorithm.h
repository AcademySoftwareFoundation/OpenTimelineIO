// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/stack.h"
#include "opentimelineio/track.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief Flatten a stack down to a single track.
OPENTIMELINEIO_EXPORT
Track* flatten_stack(Stack* in_stack, ErrorStatus* error_status = nullptr);

/// @brief Flatten a list of tracks down to a single track.
OPENTIMELINEIO_EXPORT Track* flatten_stack(
    std::vector<Track*> const& tracks,
    ErrorStatus*               error_status = nullptr);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
