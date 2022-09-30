// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/stack.h"
#include "opentimelineio/track.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

Track* flatten_stack(Stack* in_stack, ErrorStatus* error_status = nullptr);
Track* flatten_stack(
    std::vector<Track*> const& tracks,
    ErrorStatus*               error_status = nullptr);

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
