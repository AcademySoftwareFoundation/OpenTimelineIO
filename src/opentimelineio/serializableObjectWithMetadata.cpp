// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/serializableObjectWithMetadata.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

SerializableObjectWithMetadata::SerializableObjectWithMetadata(
    std::string const&   name,
    AnyDictionary const& metadata)
    : _name(name)
    , _metadata(metadata)
{}

SerializableObjectWithMetadata::~SerializableObjectWithMetadata()
{}

bool
SerializableObjectWithMetadata::read_from(Reader& reader)
{
    return reader.read_if_present("metadata", &_metadata)
           && reader.read_if_present("name", &_name)
           && SerializableObject::read_from(reader);
}

void
SerializableObjectWithMetadata::write_to(Writer& writer) const
{
    SerializableObject::write_to(writer);
    writer.write("metadata", _metadata);
    writer.write("name", _name);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
