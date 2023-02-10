// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/version.h"

#include <ImathBox.h>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

using namespace opentime;

class MediaReference : public SerializableObjectWithMetadata
{
public:
    struct Schema
    {
        static auto constexpr name   = "MediaReference";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    MediaReference(
        std::string const&            name                   = std::string(),
        optional<TimeRange> const&    available_range        = nullopt,
        AnyDictionary const&          metadata               = AnyDictionary(),
        optional<Imath::Box2d> const& available_image_bounds = nullopt);

    optional<TimeRange> available_range() const noexcept
    {
        return _available_range;
    }

    void set_available_range(optional<TimeRange> const& available_range)
    {
        _available_range = available_range;
    }

    virtual bool is_missing_reference() const;

    optional<Imath::Box2d> available_image_bounds() const
    {
        return _available_image_bounds;
    }

    void set_available_image_bounds(
        optional<Imath::Box2d> const& available_image_bounds)
    {
        _available_image_bounds = available_image_bounds;
    }

protected:
    ~MediaReference() override;

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    optional<TimeRange>    _available_range;
    optional<Imath::Box2d> _available_image_bounds;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
