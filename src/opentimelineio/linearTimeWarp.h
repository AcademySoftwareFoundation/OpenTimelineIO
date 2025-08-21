// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/timeEffect.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief A time warp that applies a linear speed up or slow down across the entire clip.
class OPENTIMELINEIO_EXPORT LinearTimeWarp : public TimeEffect
{
public:
    /// @brief This struct provides the LinearTimeWarp schema.
    struct Schema
    {
        static auto constexpr name   = "LinearTimeWarp";
        static int constexpr version = 1;
    };

    using Parent = TimeEffect;

    /// @brief Create a new linear time warp effect.
    ///
    /// @param name The name of the time effect object.
    /// @param effect_name The name of the time effect.
    /// @param time_scalar The amount to scale the time.
    /// @param metadata The metadata for the time effect.
    LinearTimeWarp(
        std::string const&   name        = std::string(),
        std::string const&   effect_name = std::string(),
        double               time_scalar = 1,
        AnyDictionary const& metadata    = AnyDictionary());

    /// @brief Return the amount to scale the time.
    double time_scalar() const noexcept { return _time_scalar; }

    /// @brief Set the amount to scale the time.
    void set_time_scalar(double time_scalar) noexcept
    {
        _time_scalar = time_scalar;
    }

protected:
    virtual ~LinearTimeWarp();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    double _time_scalar;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
