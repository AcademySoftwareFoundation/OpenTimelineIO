// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/mediaReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

MediaReference::MediaReference(
    std::string const&                 name,
    std::optional<TimeRange> const&    available_range,
    AnyDictionary const&               metadata,
    std::optional<Imath::Box2d> const& available_image_bounds)
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

bool
MediaReference::read_from(Reader& reader)
{
    return reader.read_if_present("available_range", &_available_range)
           && reader.read_if_present(
               "available_image_bounds",
               &_available_image_bounds)
           && Parent::read_from(reader);
}

void
MediaReference::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("available_range", _available_range);
    writer.write("available_image_bounds", _available_image_bounds);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
