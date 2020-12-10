#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/effect.h"
#include "opentime/timeRange.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class TimeEffect : public Effect {
public:
    struct Schema {
        static auto constexpr name = "TimeEffect";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    TimeEffect(std::string const& name = std::string(),
               std::string const& effect_name = std::string(),
               AnyDictionary const& metadata = AnyDictionary());

    virtual TimeRange output_range(TimeRange input_range, ErrorStatus* error_status) const;
    
protected:
    virtual ~TimeEffect();

};

} }
