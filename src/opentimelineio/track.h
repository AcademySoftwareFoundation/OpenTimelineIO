// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/composition.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

enum TrimPolicy
{
    IgnoreTimeEffects = 0,
    HonorTimeEffectsExactly,
    HonorTimeEffectsWithSnapping
};

class Clip;

class Track : public Composition
{
public:
    struct Kind
    {
        static auto constexpr video = "Video";
        static auto constexpr audio = "Audio";
    };

    enum NeighborGapPolicy
    {
        never              = 0,
        around_transitions = 1
    };

    struct Schema
    {
        static auto constexpr name   = "Track";
        static int constexpr version = 1;
    };

    using Parent = Composition;

    Track(
        std::string const&         name         = std::string(),
        optional<TimeRange> const& source_range = nullopt,
        std::string const&                      = Kind::video,
        AnyDictionary const& metadata           = AnyDictionary());

    std::string kind() const noexcept { return _kind; }

    void set_kind(std::string const& kind) { _kind = kind; }

    TimeRange range_of_child_at_index(
        int          index,
        ErrorStatus* error_status = nullptr) const override;
    TimeRange trimmed_range_of_child_at_index(
        int          index,
        ErrorStatus* error_status = nullptr) const override;
    TimeRange
    available_range(ErrorStatus* error_status = nullptr) const override;

    std::pair<optional<RationalTime>, optional<RationalTime>> handles_of_child(
        Composable const* child,
        ErrorStatus*      error_status = nullptr) const override;

    std::pair<Retainer<Composable>, Retainer<Composable>> neighbors_of(
        Composable const* item,
        ErrorStatus*      error_status = nullptr,
        NeighborGapPolicy insert_gap   = NeighborGapPolicy::never) const;

    std::map<Composable*, TimeRange>
    range_of_all_children(ErrorStatus* error_status = nullptr) const override;

    optional<IMATH_NAMESPACE::Box2d>
    available_image_bounds(ErrorStatus* error_status) const override;

    // Find child clips.
    //
    // An optional search_range may be provided to limit the search.
    //
    // The search is recursive unless shallow_search is set to true.
    std::vector<Retainer<Clip>> find_clips(
        ErrorStatus*               error_status   = nullptr,
        optional<TimeRange> const& search_range   = nullopt,
        bool                       shallow_search = false) const;

protected:
    virtual ~Track();

    std::string composition_kind() const override;

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string _kind;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
