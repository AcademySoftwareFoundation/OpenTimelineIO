// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/indexStreamAddress.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

IndexStreamAddress::IndexStreamAddress(int64_t index)
    : Parent()
    , _index(index)
{}

IndexStreamAddress::~IndexStreamAddress()
{}

bool
IndexStreamAddress::read_from(Reader& reader)
{
    return reader.read("index", &_index) && Parent::read_from(reader);
}

void
IndexStreamAddress::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("index", _index);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
