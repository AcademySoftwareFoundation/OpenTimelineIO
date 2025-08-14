// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/effect.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief Base class for all effects that alter the timing of an item.
class OPENTIMELINEIO_EXPORT TimeEffect : public Effect
{
public:
    /// @brief This struct provides the TimeEffect schema.
    struct Schema
    {
        static auto constexpr name   = "TimeEffect";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    /// @brief Create a new time effect.
    ///
    /// @param name The name of the object.
    /// @param effect_name The time effect name.
    /// @param metadata The metadata for the time effect.
    TimeEffect(
        std::string const&   name        = std::string(),
        std::string const&   effect_name = std::string(),
        AnyDictionary const& metadata    = AnyDictionary());

protected:
    virtual ~TimeEffect();
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
