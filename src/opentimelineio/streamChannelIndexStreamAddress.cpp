// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/streamChannelIndexStreamAddress.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

StreamChannelIndexStreamAddress::StreamChannelIndexStreamAddress(
    int64_t stream_index,
    int64_t channel_index)
    : Parent()
    , _stream_index(stream_index)
    , _channel_index(channel_index)
{}

StreamChannelIndexStreamAddress::~StreamChannelIndexStreamAddress()
{}

bool
StreamChannelIndexStreamAddress::read_from(Reader& reader)
{
    return reader.read("stream_index",  &_stream_index)
        && reader.read("channel_index", &_channel_index)
        && Parent::read_from(reader);
}

void
StreamChannelIndexStreamAddress::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("stream_index",  _stream_index);
    writer.write("channel_index", _channel_index);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
