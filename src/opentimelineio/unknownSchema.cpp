// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/unknownSchema.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

UnknownSchema::UnknownSchema(
    std::string const& original_schema_name,
    int                original_schema_version)
    : _original_schema_name(original_schema_name)
    , _original_schema_version(original_schema_version)
{}

UnknownSchema::~UnknownSchema()
{}

bool
UnknownSchema::read_from(Reader& reader)
{
    _data.swap(reader._dict);
    _data.erase("OTIO_SCHEMA");
    return true;
}

void
UnknownSchema::write_to(Writer& writer) const
{
    for (auto e: _data)
    {
        writer.write(e.first, e.second);
    }
}

std::string
UnknownSchema::_schema_name_for_reference() const
{
    return _original_schema_name;
}

bool
UnknownSchema::is_unknown_schema() const
{
    return true;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
