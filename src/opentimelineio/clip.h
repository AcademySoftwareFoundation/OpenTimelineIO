#pragma once

#include "opentimelineio/item.h"
#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Clip : public Item
{
public:
    struct MediaRepresentation
    {
        static char constexpr default_media[]         = "DEFAULT_MEDIA";
        static char constexpr high_resolution_media[] = "HIGH_RESOLUTION_MEDIA";
        static char constexpr proxy_resolution_media[] =
            "PROXY_RESOLUTION_MEDIA";
    };

    struct Schema
    {
        static auto constexpr name   = "Clip";
        static int constexpr version = 2;
    };

    using Parent = Item;

    Clip(
        std::string const&         name            = std::string(),
        MediaReference*            media_reference = nullptr,
        optional<TimeRange> const& source_range    = nullopt,
        AnyDictionary const&       metadata        = AnyDictionary(),
        std::string const&         active_media_reference =
            MediaRepresentation::default_media);

    void            set_media_reference(MediaReference* media_reference);
    MediaReference* media_reference() const noexcept;

    using MediaReferences = std::map<std::string, MediaReference*>;

    MediaReferences media_references() const noexcept;
    void set_media_references(MediaReferences const& media_references) noexcept;

    std::string active_media_reference() const noexcept;
    void set_active_media_reference(std::string const& new_active) noexcept;

    virtual TimeRange
    available_range(ErrorStatus* error_status = nullptr) const;

    virtual optional<Imath::Box2d>
    available_image_bounds(ErrorStatus* error_status) const;

protected:
    virtual ~Clip();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::map<std::string, Retainer<MediaReference>> _media_references;
    std::string                                     _active_media_reference;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
