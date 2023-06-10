// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class MissingReference final : public MediaReference
{
public:
    struct Schema
    {
        static auto constexpr name   = "MissingReference";
        static int constexpr version = 1;
    };

    using Parent = MediaReference;

    MissingReference(
        std::string const&                           name                   = std::string(),
        std::optional<TimeRange> const&              available_range        = std::nullopt,
        AnyDictionary const&                         metadata               = AnyDictionary(),
        std::optional<IMATH_NAMESPACE::Box2d> const& available_image_bounds = std::nullopt);

    bool is_missing_reference() const override;

protected:
    virtual ~MissingReference();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
