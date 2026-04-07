// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/stringStreamAddress.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

StringStreamAddress::StringStreamAddress(std::string const& address)
    : Parent()
    , _address(address)
{}

StringStreamAddress::~StringStreamAddress()
{}

bool
StringStreamAddress::read_from(Reader& reader)
{
    return reader.read("address", &_address) && Parent::read_from(reader);
}

void
StringStreamAddress::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("address", _address);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
