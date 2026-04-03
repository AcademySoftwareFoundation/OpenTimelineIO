// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/streamMapper.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

StreamMapper::StreamMapper(
    std::string const&   name,
    std::string const&   effect_name,
    StreamMap const&     stream_map,
    AnyDictionary const& metadata)
    : Parent(name, effect_name, metadata)
    , _stream_map(stream_map)
{}

StreamMapper::~StreamMapper()
{}

bool
StreamMapper::read_from(Reader& reader)
{
    return reader.read_if_present("stream_map", &_stream_map)
           && Parent::read_from(reader);
}

void
StreamMapper::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("stream_map", _stream_map);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
