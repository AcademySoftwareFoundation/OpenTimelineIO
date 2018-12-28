#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/stack.h"
#include "opentimelineio/track.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
Track* flatten_stack(Stack* in_stack, ErrorStatus* error_status);
Track* flatten_stack(std::vector<Track*> const& tracks, ErrorStatus* error_status);
    
} }
