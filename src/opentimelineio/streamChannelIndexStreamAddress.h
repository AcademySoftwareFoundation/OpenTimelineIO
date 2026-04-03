// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/streamAddress.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief Addresses a stream by track index and channel index within that track.
///
/// Use this for container formats that organise media into discrete tracks,
/// each of which may contain one or more channels — for example MP4/MOV and
/// MXF.  The `stream_index` identifies the track and the `channel_index`
/// identifies the channel within that track.
class OTIO_API_TYPE StreamChannelIndexStreamAddress : public StreamAddress
{
public:
    /// @brief This struct provides the StreamChannelIndexStreamAddress schema.
    struct Schema
    {
        static char constexpr name[]  = "StreamChannelIndexStreamAddress";
        static int constexpr version = 1;
    };

    using Parent = StreamAddress;

    /// @brief Create a new StreamChannelIndexStreamAddress.
    ///
    /// @param stream_index  Integer index of the media track within its
    ///   container (e.g. the ffmpeg/libav stream index).
    /// @param channel_index Integer index of the channel within that track.
    OTIO_API explicit StreamChannelIndexStreamAddress(
        int64_t stream_index  = 0,
        int64_t channel_index = 0);

    /// @brief Return the stream (track) index.
    OTIO_API int64_t stream_index()  const noexcept { return _stream_index; }

    /// @brief Set the stream (track) index.
    OTIO_API void set_stream_index(int64_t stream_index) noexcept
    {
        _stream_index = stream_index;
    }

    /// @brief Return the channel index within the stream.
    OTIO_API int64_t channel_index() const noexcept { return _channel_index; }

    /// @brief Set the channel index within the stream.
    OTIO_API void set_channel_index(int64_t channel_index) noexcept
    {
        _channel_index = channel_index;
    }

protected:
    virtual ~StreamChannelIndexStreamAddress();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    int64_t _stream_index;
    int64_t _channel_index;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
