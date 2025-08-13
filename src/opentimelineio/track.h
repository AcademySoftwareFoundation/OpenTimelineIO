// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/composition.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Clip;

/// @brief A track is a composition of a certain kind, like video or audio.
class Track : public Composition
{
public:
    /// @brief This struct provides the base set of kinds of tracks.
    struct Kind
    {
        static auto constexpr video = "Video";
        static auto constexpr audio = "Audio";
    };

    /// @brief This enumeration provides the neighbor gap policy.
    enum NeighborGapPolicy
    {
        never              = 0,
        around_transitions = 1
    };

    /// @brief This struct provides the Track schema.
    struct Schema
    {
        static auto constexpr name   = "Track";
        static int constexpr version = 1;
    };

    using Parent = Composition;

    /// @brief Create a new track.
    ///
    /// @param name The track name.
    /// @param source_range The source range of the track.
    /// @param kind The kind of track.
    /// @param metadata The metadata for the track.
    Track(
        std::string const&              name         = std::string(),
        std::optional<TimeRange> const& source_range = std::nullopt,
        std::string const&              kind         = Kind::video,
        AnyDictionary const&            metadata     = AnyDictionary(),
        std::optional<Color> const&     color        = std::nullopt);

    /// @brief Return this kind of track.
    std::string kind() const noexcept { return _kind; }

    /// @brief Set this kind of track.
    void set_kind(std::string const& kind) { _kind = kind; }

    TimeRange range_of_child_at_index(
        int          index,
        ErrorStatus* error_status = nullptr) const override;
    TimeRange trimmed_range_of_child_at_index(
        int          index,
        ErrorStatus* error_status = nullptr) const override;
    TimeRange
    available_range(ErrorStatus* error_status = nullptr) const override;

    std::pair<std::optional<RationalTime>, std::optional<RationalTime>>
    handles_of_child(
        Composable const* child,
        ErrorStatus*      error_status = nullptr) const override;

    /// @brief Return the neighbors of the given item.
    std::pair<Retainer<Composable>, Retainer<Composable>> neighbors_of(
        Composable const* item,
        ErrorStatus*      error_status = nullptr,
        NeighborGapPolicy insert_gap   = NeighborGapPolicy::never) const;

    std::map<Composable*, TimeRange>
    range_of_all_children(ErrorStatus* error_status = nullptr) const override;

    std::optional<IMATH_NAMESPACE::Box2d>
    available_image_bounds(ErrorStatus* error_status) const override;

protected:
    virtual ~Track();

    std::string composition_kind() const override;

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string _kind;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
