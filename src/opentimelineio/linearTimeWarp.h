#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/timeEffect.h"
#include "opentime/timeRange.h"
#include "opentime/timeTransform.h"
#include "opentime/rationalTime.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class LinearTimeWarp : public TimeEffect {
public:
    struct Schema {
        static auto constexpr name = "LinearTimeWarp";
        static int constexpr version = 1;
    };

    using Parent = TimeEffect;

    LinearTimeWarp(std::string const& name = std::string(),
                   std::string const& effect_name = std::string(),
                   double time_scalar = 1,
                   AnyDictionary const& metadata = AnyDictionary());

    double time_scalar() const {
        return _time_scalar;
    }

    void set_time_scalar(double time_scalar) {
        // TODO: Is there a concept of validation within set methods?
        // I think the only invalid value is 0 (use a freeze frame)
        _time_scalar = time_scalar;
    }

    virtual TimeRange output_range(TimeRange input_range,  ErrorStatus* error_status) const {
        return TimeTransform(
            RationalTime(),
            // TODO: Does time_scalar in LinearTimeWarp mean
            // "make it this much faster"
            // or "make it this much slower"?
            // e.g. is 2.0 twice the speed or twice the length?
            1 / _time_scalar
        ).applied_to(
            TimeRange(RationalTime(), input_range.duration())
        );
    }

protected:
    virtual ~LinearTimeWarp();

    virtual bool read_from(Reader&) ;
    virtual void write_to(Writer&) const;

private:
    double _time_scalar;
};

} }
