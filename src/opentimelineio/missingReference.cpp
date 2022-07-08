// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/missingReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

MissingReference::MissingReference(
    std::string const&            name,
    optional<TimeRange> const&    available_range,
    AnyDictionary const&          metadata,
    optional<Imath::Box2d> const& available_image_bounds)
    : Parent(name, available_range, metadata, available_image_bounds)
{}

MissingReference::~MissingReference()
{}

bool
MissingReference::is_missing_reference() const
{
    return true;
}

bool
MissingReference::read_from(Reader& reader)
{
    return Parent::read_from(reader);
}

void
MissingReference::write_to(Writer& writer) const
{
    Parent::write_to(writer);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
