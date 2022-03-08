#include "opentimelineio/clip.h"
#include "opentimelineio/missingReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

char constexpr Clip::MediaRepresentation::default_media[];
char constexpr Clip::MediaRepresentation::high_resolution_media[];
char constexpr Clip::MediaRepresentation::proxy_resolution_media[];

Clip::Clip(
    std::string const&         name,
    MediaReference*            media_reference,
    optional<TimeRange> const& source_range,
    AnyDictionary const&       metadata,
    std::string const&         active_media_reference)
    : Parent{ name, source_range, metadata }
    , _active_media_reference(active_media_reference)
{
    set_media_reference(media_reference);
}

Clip::~Clip()
{}

MediaReference*
Clip::media_reference() const noexcept
{
    auto active = _media_references.find(_active_media_reference);
    return active == _media_references.end() || !active->second
               ? nullptr
               : active->second;
}

Clip::MediaReferences
Clip::media_references() const noexcept
{
    MediaReferences result;
    for (auto const& m: _media_references)
    {
        result.insert(
            { m.first, dynamic_retainer_cast<MediaReference>(m.second) });
    }
    return result;
}

void
Clip::set_media_references(MediaReferences const& media_references) noexcept
{
    _media_references.clear();
    for (auto const& m: media_references)
    {
        _media_references[m.first] = m.second;
    }
}

std::string
Clip::active_media_reference() const noexcept
{
    return _active_media_reference;
}

void
Clip::set_active_media_reference(std::string const& new_active) noexcept
{
    _active_media_reference = new_active;
}

void
Clip::set_media_reference(MediaReference* media_reference)
{
    _media_references[_active_media_reference] =
        media_reference ? media_reference : new MissingReference;
}

bool
Clip::read_from(Reader& reader)
{
    return reader.read("media_references", &_media_references) &&
           reader.read("active_media_reference", &_active_media_reference) &&
           Parent::read_from(reader);
}

void
Clip::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("media_references", _media_references);
    writer.write("active_media_reference", _active_media_reference);
}

TimeRange
Clip::available_range(ErrorStatus* error_status) const
{
    auto active_media = media_reference();
    if (!active_media)
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::CANNOT_COMPUTE_AVAILABLE_RANGE,
                "No media reference set on clip",
                this);
        }
        return TimeRange();
    }

    if (!active_media->available_range())
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::CANNOT_COMPUTE_AVAILABLE_RANGE,
                "No available_range set on media reference on clip",
                this);
        }
        return TimeRange();
    }

    return active_media->available_range().value();
}

optional<Imath::Box2d>
Clip::available_image_bounds(ErrorStatus* error_status) const
{
    auto active_media = media_reference();
    if (!active_media)
    {
        *error_status = ErrorStatus(
            ErrorStatus::CANNOT_COMPUTE_BOUNDS,
            "No image bounds set on clip",
            this);
        return optional<Imath::Box2d>();
    }

    if (!active_media->available_image_bounds())
    {
        *error_status = ErrorStatus(
            ErrorStatus::CANNOT_COMPUTE_BOUNDS,
            "No image bounds set on media reference on clip",
            this);
        return optional<Imath::Box2d>();
    }

    return active_media->available_image_bounds();
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
