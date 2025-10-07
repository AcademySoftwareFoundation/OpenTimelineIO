// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/stack.h"
#include "opentimelineio/track.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Clip;

/// @brief A timeline contains a stack of tracks.
class Timeline : public SerializableObjectWithMetadata
{
public:
    /// @brief This struct provides the Timeline schema.
    struct Schema
    {
        static auto constexpr name   = "Timeline";
        static int constexpr version = 2;
    };

    using Parent = SerializableObjectWithMetadata;

    /// @brief Create a new timelime.
    ///
    /// @param name The timeline name.
    /// @param global_start_time The global start time of the timeline.
    /// @param canvas_size The dimensions of the target canvas
    /// @param metadata The metadata for the timeline.
    Timeline(
        std::string const&                  name              = std::string(),
        std::optional<RationalTime>         global_start_time = std::nullopt,
        std::optional<IMATH_NAMESPACE::V2d> canvas_size       = std::nullopt,
        AnyDictionary const&                metadata          = AnyDictionary());

    /// @brief Return the timeline stack.
    Stack* tracks() const noexcept { return _tracks; }

    /*
    Stack* tracks() {
        return _tracks;
    }*/

    /// @brief Set the timeline stack.
    void set_tracks(Stack* stack);

    /// @brief Return the global start time.
    std::optional<RationalTime> global_start_time() const noexcept
    {
        return _global_start_time;
    }

    /// @brief Set the global start time.
    void
    set_global_start_time(std::optional<RationalTime> const& global_start_time)
    {
        _global_start_time = global_start_time;
    }

    /// @brief Return the canvas size
    std::optional<IMATH_NAMESPACE::V2d> canvas_size() const noexcept
    {
        return _canvas_size;
    }

    /// @brief Set the canvas size
    void
    set_canvas_size(std::optional<IMATH_NAMESPACE::V2d> const& canvas_size)
    {
        _canvas_size = canvas_size;
    }

    /// @brief Return the duration of the timeline.
    RationalTime duration(ErrorStatus* error_status = nullptr) const
    {
        return _tracks.value->duration(error_status);
    }

    /// @brief Return the range of the given child.
    TimeRange range_of_child(
        Composable const* child,
        ErrorStatus*      error_status = nullptr) const
    {
        return _tracks.value->range_of_child(child, error_status);
    }

    /// @brief Return the list of audio tracks.
    std::vector<Track*> audio_tracks() const;

    /// @brief Return the list of video tracks.
    std::vector<Track*> video_tracks() const;

    /// @brief Find child clips.
    ///
    /// @param error_status The return status.
    /// @param search_range An optional range to limit the search.
    /// @param shallow_search The search is recursive unless shallow_search is
    /// set to true.
    std::vector<Retainer<Clip>> find_clips(
        ErrorStatus*                    error_status   = nullptr,
        std::optional<TimeRange> const& search_range   = std::nullopt,
        bool                            shallow_search = false) const;

    /// @brief Find child objects that match the given template type.
    ///
    /// @param error_status The return status.
    /// @param search_range An optional range to limit the search.
    /// @param shallow_search The search is recursive unless shallow_search is
    /// set to true.
    template <typename T = Composable>
    std::vector<Retainer<T>> find_children(
        ErrorStatus*             error_status   = nullptr,
        std::optional<TimeRange> search_range   = std::nullopt,
        bool                     shallow_search = false) const;

    /// @brief Return the spatial bounds of the timeline.
    std::optional<IMATH_NAMESPACE::Box2d>
    available_image_bounds(ErrorStatus* error_status) const
    {
        return _tracks.value->available_image_bounds(error_status);
    }

    /// @brief Invalidate the cache.
    void invalidate_cache() const;

protected:
    virtual ~Timeline();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::optional<RationalTime>         _global_start_time;
    std::optional<IMATH_NAMESPACE::V2d> _canvas_size;
    Retainer<Stack>                     _tracks;
};

template <typename T>
inline std::vector<SerializableObject::Retainer<T>>
Timeline::find_children(
    ErrorStatus*             error_status,
    std::optional<TimeRange> search_range,
    bool                     shallow_search) const
{
    return _tracks.value->find_children<T>(
        error_status,
        search_range,
        shallow_search);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
