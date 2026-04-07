// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/streamSelector.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

StreamSelector::StreamSelector(
    std::string const&              name,
    std::string const&              effect_name,
    std::vector<std::string> const& output_streams,
    AnyDictionary const&            metadata)
    : Parent(name, effect_name, metadata)
    , _output_streams(output_streams)
{}

StreamSelector::~StreamSelector()
{}

bool
StreamSelector::read_from(Reader& reader)
{
    return reader.read_if_present("output_streams", &_output_streams)
           && Parent::read_from(reader);
}

void
StreamSelector::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("output_streams", _output_streams);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
