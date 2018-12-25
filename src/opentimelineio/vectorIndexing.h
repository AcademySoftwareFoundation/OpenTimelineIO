#pragma once

#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
template <typename V>
inline int adjusted_vector_index(int index, V const& vec) {
    return index < 0 ? int(vec.size()) + index : index;
}
    
} }
