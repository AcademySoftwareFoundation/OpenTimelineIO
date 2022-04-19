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

    explicit MediaReference() {}
    
    MediaReference(
        std::string const&            name,
        AnyDictionary const&          metadata               = AnyDictionary());

    MediaReference(
        std::string const&            name,
        optional<TimeRange> const&    available_range        = nullopt,
        AnyDictionary const&          metadata               = AnyDictionary(),
        optional<Imath::Box2d> const& available_image_bounds = nullopt);

    virtual optional<TimeRange> available_range() const noexcept
    {
        return _available_range;
    }

    virtual void set_available_range(optional<TimeRange> const& available_range)
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
    virtual ~MediaReference();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

    optional<TimeRange>    _available_range;
    optional<Imath::Box2d> _available_image_bounds;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
