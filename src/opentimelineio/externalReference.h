// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class ExternalReference final : public MediaReference
{
public:
    struct Schema
    {
        static auto constexpr name   = "ExternalReference";
        static int constexpr version = 1;
    };

    using Parent = MediaReference;

    ExternalReference(
        std::string const&                           target_url             = std::string(),
        std::optional<TimeRange> const&              available_range        = std::nullopt,
        AnyDictionary const&                         metadata               = AnyDictionary(),
        std::optional<IMATH_NAMESPACE::Box2d> const& available_image_bounds = std::nullopt);

    std::string target_url() const noexcept { return _target_url; }

    void set_target_url(std::string const& target_url)
    {
        _target_url = target_url;
    }

protected:
    virtual ~ExternalReference();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string _target_url;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
