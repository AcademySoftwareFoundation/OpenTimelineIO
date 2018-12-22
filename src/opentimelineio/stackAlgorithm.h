#pragma once
#include "opentimelineio/stack.h"
#include "opentimelineio/track.h"

Track* flatten_stack(Stack* in_stack, ErrorStatus* error_status);
