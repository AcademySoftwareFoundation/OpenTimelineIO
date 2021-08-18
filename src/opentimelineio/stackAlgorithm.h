#pragma once

#include "opentimelineio/stack.h"
#include "opentimelineio/track.h"
#include "opentimelineio/version.h"

namespace opentimelineio
{
namespace OPENTIMELINEIO_VERSION
{

Track* flatten_stack(Stack* in_stack, ErrorStatus* error_status);
Track*
flatten_stack(std::vector<Track*> const& tracks, ErrorStatus* error_status);

} // namespace OPENTIMELINEIO_VERSION
} // namespace opentimelineio
