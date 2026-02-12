// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief A marker indicates a marked range of time on an item in a timeline,
/// usually with a name, color or other metadata.
///
/// The marked range may have a zero duration. The marked range is in the
/// owning item's time coordinate system.
class OTIO_API_TYPE Marker : public SerializableObjectWithMetadata
{
public:
    /// @brief This struct provides the base set of colors.
    struct Color
    {
        static auto constexpr pink    = "PINK";
        static auto constexpr red     = "RED";
        static auto constexpr orange  = "ORANGE";
        static auto constexpr yellow  = "YELLOW";
        static auto constexpr green   = "GREEN";
        static auto constexpr cyan    = "CYAN";
        static auto constexpr blue    = "BLUE";
        static auto constexpr purple  = "PURPLE";
        static auto constexpr magenta = "MAGENTA";
        static auto constexpr black   = "BLACK";
        static auto constexpr white   = "WHITE";
    };

    /// @brief This struct provides the Marker schema.
    struct Schema
    {
        static auto constexpr name   = "Marker";
        static int constexpr version = 2;
    };

    using Parent = SerializableObjectWithMetadata;

    /// @brief Create a new marker.
    ///
    /// @param name The name of the marker.
    /// @param marked_range The time range of the marker.
    /// @param color The color associated with the marker.
    /// @param metadata The metadata for the marker.
    /// @param comment The text comment for the marker.
    OTIO_API Marker(
        std::string const&   name         = std::string(),
        TimeRange const&     marked_range = TimeRange(),
        std::string const&   color        = Color::green,
        AnyDictionary const& metadata     = AnyDictionary(),
        std::string const&   comment      = std::string());

    /// @brief Return the marker color.
    std::string color() const noexcept { return _color; }

    /// @brief Set the marker color.
    void set_color(std::string const& color) { _color = color; }

    /// @brief Return the marker time range.
    TimeRange marked_range() const noexcept { return _marked_range; }

    /// @brief Set the marker time range.
    void set_marked_range(TimeRange const& marked_range) noexcept
    {
        _marked_range = marked_range;
    }

    /// @brief Return the marker comment.
    std::string comment() const noexcept { return _comment; }

    /// @brief Set the marker comment.
    void set_comment(std::string const& comment) { _comment = comment; }

protected:
    virtual ~Marker();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string _color;
    TimeRange   _marked_range;
    std::string _comment;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
