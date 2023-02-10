// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/stack.h"
#include "opentimelineio/track.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Clip;

class Timeline : public SerializableObjectWithMetadata
{
public:
    struct Schema
    {
        static auto constexpr name   = "Timeline";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    Timeline(
        std::string const&     name              = std::string(),
        optional<RationalTime> global_start_time = nullopt,
        AnyDictionary const&   metadata          = AnyDictionary());

    Stack* tracks() const noexcept { return _tracks; }

    /*
    Stack* tracks() {
        return _tracks;
    }*/

    void set_tracks(Stack* stack);

    optional<RationalTime> global_start_time() const noexcept
    {
        return _global_start_time;
    }

    void set_global_start_time(optional<RationalTime> const& global_start_time)
    {
        _global_start_time = global_start_time;
    }

    RationalTime duration(ErrorStatus* error_status = nullptr) const
    {
        return _tracks.value->duration(error_status);
    }

    TimeRange range_of_child(
        Composable const* child,
        ErrorStatus*      error_status = nullptr) const
    {
        return _tracks.value->range_of_child(child, error_status);
    }

    std::vector<Track*> audio_tracks() const;
    std::vector<Track*> video_tracks() const;

    // Find child clips.
    //
    // An optional search_range may be provided to limit the search.
    //
    // The search is recursive unless shallow_search is set to true.
    std::vector<Retainer<Clip>> find_clips(
        ErrorStatus*               error_status   = nullptr,
        optional<TimeRange> const& search_range   = nullopt,
        bool                       shallow_search = false) const;

    // Find child objects that match the given template type.
    //
    // An optional search_time may be provided to limit the search.
    //
    // The search is recursive unless shallow_search is set to true.
    template <typename T = Composable>
    std::vector<Retainer<T>> find_children(
        ErrorStatus*        error_status   = nullptr,
        optional<TimeRange> search_range   = nullopt,
        bool                shallow_search = false) const;

    optional<Imath::Box2d>
    available_image_bounds(ErrorStatus* error_status) const
    {
        return _tracks.value->available_image_bounds(error_status);
    }

protected:
    ~Timeline() override;

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    optional<RationalTime> _global_start_time;
    Retainer<Stack>        _tracks;
};

template <typename T>
inline std::vector<SerializableObject::Retainer<T>>
Timeline::find_children(
    ErrorStatus*        error_status,
    optional<TimeRange> search_range,
    bool                shallow_search) const
{
    return _tracks.value->find_children<T>(
        error_status,
        search_range,
        shallow_search);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
