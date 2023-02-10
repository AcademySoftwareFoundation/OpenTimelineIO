// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/effect.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class TimeEffect : public Effect
{
public:
    struct Schema
    {
        static auto constexpr name   = "TimeEffect";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    TimeEffect(
        std::string const&   name        = std::string(),
        std::string const&   effect_name = std::string(),
        AnyDictionary const& metadata    = AnyDictionary());

protected:
    ~TimeEffect() override;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
