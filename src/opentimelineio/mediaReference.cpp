// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/mediaReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

MediaReference::MediaReference(
    std::string const&                           name,
    std::optional<TimeRange> const&              available_range,
    AnyDictionary const&                         metadata,
    std::optional<IMATH_NAMESPACE::Box2d> const& available_image_bounds)
    : Parent(name, metadata)
    , _available_range(available_range)
    , _available_image_bounds(available_image_bounds)
{}

MediaReference::~MediaReference()
{}

bool
MediaReference::is_missing_reference() const
{
    return false;
}

MediaReference::AvailableStreams
MediaReference::available_streams() const noexcept
{
    AvailableStreams result;
    for (auto const& s: _available_streams)
    {
        result.insert(
            { s.first, dynamic_retainer_cast<StreamInfo>(s.second) });
    }
    return result;
}

void
MediaReference::set_available_streams(AvailableStreams const& available_streams)
{
    _available_streams.clear();
    for (auto const& s: available_streams)
    {
        _available_streams[s.first] = s.second;
    }
}


bool
MediaReference::read_from(Reader& reader)
{
    return reader.read_if_present("available_range", &_available_range)
           && reader.read_if_present(
               "available_image_bounds",
               &_available_image_bounds)
           && reader.read_if_present("available_streams", &_available_streams)
           && Parent::read_from(reader);
}

void
MediaReference::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("available_range", _available_range);
    writer.write("available_image_bounds", _available_image_bounds);
    if (!_available_streams.empty())
    {
        writer.write("available_streams", _available_streams);
    }
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
