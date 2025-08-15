// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentime/timeRange.h"
#include "opentimelineio/color.h"
#include "opentimelineio/composable.h"
#include "opentimelineio/errorStatus.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Effect;
class Marker;

/// @brief An item in the timeline.
class OPENTIMELINEIO_EXPORT Item : public Composable
{
public:
    /// @brief This struct provides the Item schema.
    struct Schema
    {
        static auto constexpr name   = "Item";
        static int constexpr version = 1;
    };

    using Parent = Composable;

    /// @brief Create a new item.
    ///
    /// @param name The name of the item.
    /// @param source_range The source range of the item.
    /// @param metadata The metadata for the item.
    /// @param effects The list of effects for the item. Note that the
    /// the item keeps a retainer to each effect.
    /// @param markers The list of markers for the item. Note that the
    /// the item keeps a retainer to each marker.
    /// @param enabled Whether the item is enabled.
    Item(
        std::string const&              name         = std::string(),
        std::optional<TimeRange> const& source_range = std::nullopt,
        AnyDictionary const&            metadata     = AnyDictionary(),
        std::vector<Effect*> const&     effects      = std::vector<Effect*>(),
        std::vector<Marker*> const&     markers      = std::vector<Marker*>(),
        bool                            enabled      = true,
        std::optional<Color> const&     color        = std::nullopt);

    bool visible() const override;
    bool overlapping() const override;

    /// @brief Return whether the item is enabled.
    bool enabled() const { return _enabled; };

    /// @brief Set whether the item is enabled.
    void set_enabled(bool enabled) { _enabled = enabled; }

    /// @brief Return the source range of the item.
    std::optional<TimeRange> source_range() const noexcept
    {
        return _source_range;
    }

    /// @brief Set the source range of the item.
    void set_source_range(std::optional<TimeRange> const& source_range)
    {
        _source_range = source_range;
    }

    /// @brief Modify the list of effects.
    std::vector<Retainer<Effect>>& effects() noexcept { return _effects; }

    /// @brief Return the list of effects.
    std::vector<Retainer<Effect>> const& effects() const noexcept
    {
        return _effects;
    }

    /// @brief Modify the list of markers.
    std::vector<Retainer<Marker>>& markers() noexcept { return _markers; }

    /// @brief Return the list of markers.
    std::vector<Retainer<Marker>> const& markers() const noexcept
    {
        return _markers;
    }

    RationalTime duration(ErrorStatus* error_status = nullptr) const override;

    /// @brief Return the available range of the item.
    virtual TimeRange
    available_range(ErrorStatus* error_status = nullptr) const;

    /// @brief Return the trimmed range of the item.
    TimeRange trimmed_range(ErrorStatus* error_status = nullptr) const
    {
        return _source_range ? *_source_range : available_range(error_status);
    }

    /// @brief Return the visible range of the item.
    TimeRange visible_range(ErrorStatus* error_status = nullptr) const;

    /// @brief Return the trimmed range of the item in the parent's time.
    std::optional<TimeRange>
    trimmed_range_in_parent(ErrorStatus* error_status = nullptr) const;

    /// @brief Return the range of the item in the parent's time.
    TimeRange range_in_parent(ErrorStatus* error_status = nullptr) const;

    /// @brief Return the time transformed to another item in the hierarchy.
    RationalTime transformed_time(
        RationalTime time,
        Item const*  to_item,
        ErrorStatus* error_status = nullptr) const;

    /// @brief Return the time range transformed to another item in the hierarchy.
    TimeRange transformed_time_range(
        TimeRange    time_range,
        Item const*  to_item,
        ErrorStatus* error_status = nullptr) const;

    std::optional<Color> color() const noexcept
    {
        return _color;
    }

    /// @brief Set the color of the item.
    void set_color(std::optional<Color> const& color)
    {
        _color = color;
    }

protected:
    virtual ~Item();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::optional<TimeRange>      _source_range;
    std::vector<Retainer<Effect>> _effects;
    std::vector<Retainer<Marker>> _markers;
    std::optional<Color>          _color;
    bool                          _enabled;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
