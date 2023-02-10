// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/linearTimeWarp.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class FreezeFrame : public LinearTimeWarp
{
public:
    struct Schema
    {
        static auto constexpr name   = "FreezeFrame";
        static int constexpr version = 1;
    };

    using Parent = LinearTimeWarp;

    FreezeFrame(
        std::string const&   name     = std::string(),
        AnyDictionary const& metadata = AnyDictionary());

protected:
    ~FreezeFrame() override;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
