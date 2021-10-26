#pragma once

#include "opentimelineio/timeEffect.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class LinearTimeWarp : public TimeEffect
{
public:
    struct Schema
    {
        static auto constexpr name   = "LinearTimeWarp";
        static int constexpr version = 1;
    };

    using Parent = TimeEffect;

    LinearTimeWarp(
        std::string const&   name        = std::string(),
        std::string const&   effect_name = std::string(),
        double               time_scalar = 1,
        AnyDictionary const& metadata    = AnyDictionary());

    double time_scalar() const noexcept { return _time_scalar; }

    void set_time_scalar(double time_scalar) noexcept
    {
        _time_scalar = time_scalar;
    }

protected:
    virtual ~LinearTimeWarp();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    double _time_scalar;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
