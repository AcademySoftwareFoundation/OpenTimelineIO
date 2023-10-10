// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/externalReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

ExternalReference::ExternalReference(
    std::string const&                      target_url,
    optional<TimeRange> const&              available_range,
    AnyDictionary const&                    metadata,
    optional<IMATH_NAMESPACE::Box2d> const& available_image_bounds)
    : Parent(std::string(), available_range, metadata, available_image_bounds)
    , _target_url(target_url)
{}

ExternalReference::~ExternalReference()
{}

bool
ExternalReference::read_from(Reader& reader)
{
    return reader.read("target_url", &_target_url) && Parent::read_from(reader);
}

void
ExternalReference::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("target_url", _target_url);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
