// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/linearTimeWarp.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief Hold the first frame of the clip for the duration of the clip.
class OPENTIMELINEIO_EXPORT FreezeFrame : public LinearTimeWarp
{
public:
    /// @brief This struct provides the FreezeFrame schema.
    struct Schema
    {
        static auto constexpr name   = "FreezeFrame";
        static int constexpr version = 1;
    };

    using Parent = LinearTimeWarp;

    /// @brief Create a new freeze frame time effect.
    ///
    /// @param name The name of the time effect.
    /// @param metadata The metadata for the time effect.
    FreezeFrame(
        std::string const&   name     = std::string(),
        AnyDictionary const& metadata = AnyDictionary());

protected:
    virtual ~FreezeFrame();
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
