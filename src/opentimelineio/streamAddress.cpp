// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/streamAddress.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

StreamAddress::StreamAddress()
    : Parent()
{}

StreamAddress::~StreamAddress()
{}

bool
StreamAddress::read_from(Reader& reader)
{
    return Parent::read_from(reader);
}

void
StreamAddress::write_to(Writer& writer) const
{
    Parent::write_to(writer);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
