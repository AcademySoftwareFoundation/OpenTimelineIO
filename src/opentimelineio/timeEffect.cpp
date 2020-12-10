#include "opentimelineio/timeEffect.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
TimeEffect::TimeEffect(std::string const& name,
                       std::string const& effect_name,
                       AnyDictionary const& metadata)
    : Parent(name, effect_name, metadata) {
}

TimeEffect::~TimeEffect() {
}

TimeRange TimeEffect::output_range(TimeRange input_range, ErrorStatus* error_status) const {
    *error_status = ErrorStatus::NOT_IMPLEMENTED;
    return TimeRange();
}

} }
