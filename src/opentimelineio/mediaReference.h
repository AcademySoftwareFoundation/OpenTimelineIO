// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/streamInfo.h"
#include "opentimelineio/version.h"

#include <Imath/ImathBox.h>
#include <map>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

using namespace opentime;

/// @brief A reference to a piece of media, for example a movie on a clip.
class OTIO_API_TYPE MediaReference : public SerializableObjectWithMetadata
{
public:
    /// @brief This struct provides the MediaReference schema.
    struct Schema
    {
        static auto constexpr name   = "MediaReference";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    /// @brief Create a new media reference.
    ///
    /// @param name The name of the media reference.
    /// @param available_range The available range of the media reference.
    /// @param metadata The metadata for the media reference.
    /// @param available_image_bounds The spatial bounds of the media reference.
    OTIO_API MediaReference(
        std::string const&              name            = std::string(),
        std::optional<TimeRange> const& available_range = std::nullopt,
        AnyDictionary const&            metadata        = AnyDictionary(),
        std::optional<IMATH_NAMESPACE::Box2d> const& available_image_bounds =
            std::nullopt);

    /// @brief Return the available range of the media reference.
    std::optional<TimeRange> available_range() const noexcept
    {
        return _available_range;
    }

    /// @brief Set the available range of the media reference.
    void set_available_range(std::optional<TimeRange> const& available_range)
    {
        _available_range = available_range;
    }

    /// @brief Return whether the reference is missing.
    virtual bool is_missing_reference() const;

    /// @brief Return the spatial bounds of the media reference.
    std::optional<IMATH_NAMESPACE::Box2d> available_image_bounds() const
    {
        return _available_image_bounds;
    }

    /// @brief Set the spatial bounds of the media reference.
    void set_available_image_bounds(
        std::optional<IMATH_NAMESPACE::Box2d> const& available_image_bounds)
    {
        _available_image_bounds = available_image_bounds;
    }

    using AvailableStreams = std::map<std::string, StreamInfo*>;

    /// @brief Return the map of available streams keyed by stream identifier.
    ///
    /// Keys should use values from `StreamInfo::Identifier` to signal "primary"
    /// streams (e.g. `StreamInfo::Identifier::monocular` for a "traditional"
    /// video).
    /// Additional streams should prefix a `StreamInfo::Identifier` value to
    /// form a key unique within that media reference (e.g. something like
    /// "music_stereo_right" could be used for a music stem provided in addition
	/// to the "primary" audio).
    /// However, keys may be any unique string —
    /// for example, spatial audio objects whose identity is only meaningful
    /// alongside positional renderomg metadata, or production audio tracks
    /// labelled as the character's lavalier mic or boom mic used for that shot.
    OTIO_API AvailableStreams available_streams() const noexcept;

    /// @brief Set the map of available streams.
    /// @see available_streams()
    OTIO_API void set_available_streams(AvailableStreams const& available_streams);

protected:
    virtual ~MediaReference();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::optional<TimeRange>                          _available_range;
    std::optional<IMATH_NAMESPACE::Box2d>             _available_image_bounds;
    std::map<std::string, Retainer<StreamInfo>>       _available_streams;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
