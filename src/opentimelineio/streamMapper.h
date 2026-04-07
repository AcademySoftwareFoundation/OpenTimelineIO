// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/effect.h"
#include "opentimelineio/version.h"

#include <map>
#include <string>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief An effect that remaps stream identifiers to new names.
///
/// Each entry in `stream_map` maps an output stream name (the key as it will
/// appear downstream) to an input stream name (the key as it appears in the
/// upstream `MediaReference::available_streams`).
///
/// A typical use is to normalize a source-specific identifier into a
/// well-known `StreamInfo::Identifier` value — for example, to expose the
/// left eye of a stereo source as the conventional monocular stream:
///
/// @code{.json}
///   {
///     "monocular": "left_eye"
///   }
/// @endcode
class OTIO_API_TYPE StreamMapper : public Effect
{
public:
    /// @brief This struct provides the StreamMapper schema.
    struct Schema
    {
        static char constexpr name[]  = "StreamMapper";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    using StreamMap = std::map<std::string, std::string>;

    /// @brief Create a new StreamMapper.
    ///
    /// @param name        The name of the effect object.
    /// @param effect_name The name of the effect.
    /// @param stream_map  Mapping of output stream name to input stream name.
    /// @param metadata    Optional metadata dictionary.
    OTIO_API StreamMapper(
        std::string const& name        = std::string(),
        std::string const& effect_name = std::string(),
        StreamMap const&   stream_map  = StreamMap(),
        AnyDictionary const& metadata  = AnyDictionary());

    /// @brief Return the stream name mapping.
    ///
    /// Keys are output stream names (as seen downstream); values are input
    /// stream names (keys in the upstream available_streams map).
    OTIO_API StreamMap const& stream_map() const noexcept { return _stream_map; }

    /// @brief Set the stream name mapping.
    OTIO_API void set_stream_map(StreamMap const& stream_map)
    {
        _stream_map = stream_map;
    }

protected:
    virtual ~StreamMapper();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    StreamMap _stream_map;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
