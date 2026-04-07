// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/streamInfo.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

StreamInfo::StreamInfo(
    std::string const&   name,
    StreamAddress* address,
    std::string const&   kind,
    AnyDictionary const& metadata)
    : Parent(name, metadata)
    , _address(address)
    , _kind(kind)
{}

StreamInfo::~StreamInfo()
{}

bool
StreamInfo::read_from(Reader& reader)
{
    return reader.read_if_present("address", &_address)
           && reader.read_if_present("kind", &_kind)
           && Parent::read_from(reader);
}

void
StreamInfo::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("address", _address);
    writer.write("kind", _kind);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
