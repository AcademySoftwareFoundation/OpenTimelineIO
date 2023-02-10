// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/composition.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Clip;

class Stack : public Composition
{
public:
    struct Schema
    {
        static auto constexpr name   = "Stack";
        static int constexpr version = 1;
    };

    using Parent = Composition;

    Stack(
        std::string const&          name         = std::string(),
        optional<TimeRange> const&  source_range = nullopt,
        AnyDictionary const&        metadata     = AnyDictionary(),
        std::vector<Effect*> const& effects      = std::vector<Effect*>(),
        std::vector<Marker*> const& markers      = std::vector<Marker*>());

    TimeRange range_of_child_at_index(
        int          index,
        ErrorStatus* error_status = nullptr) const override;
    TimeRange trimmed_range_of_child_at_index(
        int          index,
        ErrorStatus* error_status = nullptr) const override;
    TimeRange
    available_range(ErrorStatus* error_status = nullptr) const override;

    std::map<Composable*, TimeRange>
    range_of_all_children(ErrorStatus* error_status = nullptr) const override;

    optional<Imath::Box2d>
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
    ~Stack() override;

    std::string composition_kind() const override;

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
