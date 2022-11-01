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

    virtual TimeRange range_of_child_at_index(
        int          index,
        ErrorStatus* error_status = nullptr) const;
    virtual TimeRange trimmed_range_of_child_at_index(
        int          index,
        ErrorStatus* error_status = nullptr) const;
    virtual TimeRange
    available_range(ErrorStatus* error_status = nullptr) const;

    virtual std::map<Composable*, TimeRange>
    range_of_all_children(ErrorStatus* error_status = nullptr) const;

    optional<Imath::Box2d>
    available_image_bounds(ErrorStatus* error_status) const;

    // Return child clips.
    //
    // An optional search_range may be provided to limit the search.
    std::vector<Retainer<Clip>> clip_if(
        ErrorStatus*               error_status   = nullptr,
        optional<TimeRange> const& search_range   = nullopt,
        bool                       shallow_search = false) const;

    // Return all child clips recursively.
    std::vector<Retainer<Clip>> all_clips(
        ErrorStatus* error_status = nullptr) const;

protected:
    virtual ~Stack();

    virtual std::string composition_kind() const;

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
