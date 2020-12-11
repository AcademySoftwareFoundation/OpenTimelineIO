#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/timeEffect.h"
#include "opentime/rationalTime.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class FreezeFrame : public TimeEffect {
public:
    struct Schema {
        static auto constexpr name = "FreezeFrame";
        static int constexpr version = 1;
    };

    using Parent = TimeEffect;

    FreezeFrame(std::string const& name = std::string(),
                RationalTime duration = RationalTime(),
                AnyDictionary const& metadata = AnyDictionary());

    RationalTime duration() const {
        return _duration;
    }

    void set_duration(RationalTime duration) {
        _duration = duration;
    }

    virtual TimeRange output_range(TimeRange input_range,  ErrorStatus* error_status) const {
        return TimeRange(input_range.start_time(), _duration);
    }    

protected:
    virtual ~FreezeFrame();

    virtual bool read_from(Reader&) ;
    virtual void write_to(Writer&) const;

private:
    RationalTime _duration;
};

} }
