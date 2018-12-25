#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/track.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
Track* track_trimmed_to_range(Track* in_track, TimeRange trim_range, ErrorStatus* error_status);
    
} }
