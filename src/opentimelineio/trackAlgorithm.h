#pragma once

#include "opentimelineio/track.h"

Track* track_trimmed_to_range(Track* in_track, TimeRange trim_range, ErrorStatus* error_status);
