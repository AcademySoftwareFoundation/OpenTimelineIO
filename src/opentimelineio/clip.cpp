// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/clip.h"
#include "opentimelineio/missingReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

char constexpr Clip::default_media_key[];

Clip::Clip(
    std::string const&              name,
    MediaReference*                 media_reference,
    std::optional<TimeRange> const& source_range,
    AnyDictionary const&            metadata,
    std::vector<Effect*> const&     effects,
    std::vector<Marker*> const&     markers,
    std::string const&              active_media_reference_key,
    std::optional<Color> const&     color)
    : Parent{ name,    source_range,     metadata, effects,
              markers, /*enabled*/ true, color }
    , _active_media_reference_key(active_media_reference_key)
{
    set_media_reference(media_reference);
}

Clip::~Clip()
{}

MediaReference*
Clip::media_reference() const noexcept
{
    auto active = _media_references.find(_active_media_reference_key);
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

template <typename MediaRefMap>
bool
Clip::check_for_valid_media_reference_key(
    std::string const& caller,
    std::string const& key,
    MediaRefMap const& media_references,
    ErrorStatus*       error_status)
{
    auto empty_key = media_references.find("");
    if (empty_key != media_references.end())
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::MEDIA_REFERENCES_CONTAIN_EMPTY_KEY,
                caller
                    + " failed because the media references contain an empty string key",
                this);
        }
        return false;
    }

    auto found = media_references.find(key);
    if (found == media_references.end())
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::MEDIA_REFERENCES_DO_NOT_CONTAIN_ACTIVE_KEY,
                caller
                    + " failed because the media references do not contain the active key",
                this);
        }
        return false;
    }
    return true;
}

void
Clip::set_media_references(
    MediaReferences const& media_references,
    std::string const&     new_active_key,
    ErrorStatus*           error_status) noexcept
{
    if (!check_for_valid_media_reference_key(
            "set_media_references",
            new_active_key,
            media_references,
            error_status))
    {
        return;
    }

    _media_references.clear();
    for (auto const& m: media_references)
    {
        _media_references[m.first] = m.second ? m.second : new MissingReference;
    }

    _active_media_reference_key = new_active_key;
}

std::string
Clip::active_media_reference_key() const noexcept
{
    return _active_media_reference_key;
}

void
Clip::set_active_media_reference_key(
    std::string const& new_active_key,
    ErrorStatus*       error_status) noexcept
{
    if (!check_for_valid_media_reference_key(
            "set_active_media_reference_key",
            new_active_key,
            _media_references,
            error_status))
    {
        return;
    }
    _active_media_reference_key = new_active_key;
}

void
Clip::set_media_reference(MediaReference* media_reference)
{
    _media_references[_active_media_reference_key] =
        media_reference ? media_reference : new MissingReference;
}

bool
Clip::read_from(Reader& reader)
{
    return reader.read("media_references", &_media_references)
           && reader.read(
               "active_media_reference_key",
               &_active_media_reference_key)
           && Parent::read_from(reader);
}

void
Clip::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("media_references", _media_references);
    writer.write("active_media_reference_key", _active_media_reference_key);
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

std::optional<IMATH_NAMESPACE::Box2d>
Clip::available_image_bounds(ErrorStatus* error_status) const
{
    auto active_media = media_reference();

    //this code path most likely never runs since a null or empty media_reference gets
    //replaced with a placeholder value when instantiated
    if (!active_media)
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::CANNOT_COMPUTE_BOUNDS,
                "No image bounds set on clip",
                this);
        }

        return std::optional<IMATH_NAMESPACE::Box2d>();
    }

    if (!active_media->available_image_bounds())
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::CANNOT_COMPUTE_BOUNDS,
                "No image bounds set on media reference on clip",
                this);
        }

        return std::optional<IMATH_NAMESPACE::Box2d>();
    }

    return active_media->available_image_bounds();
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
