// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/version.h"

#include <Imath/ImathBox.h>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

using namespace opentime;

/// @brief A reference to a piece of media, for example a movie on a clip.
class MediaReference : public SerializableObjectWithMetadata
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
    MediaReference(
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

protected:
    virtual ~MediaReference();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::optional<TimeRange>              _available_range;
    std::optional<IMATH_NAMESPACE::Box2d> _available_image_bounds;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
