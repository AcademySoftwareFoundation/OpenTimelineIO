// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/composition.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Clip;

/// @brief A stack of items in a timeline, for example a stack of tracks in a timelime.
class Stack : public Composition
{
public:
    /// @brief This struct provides the Stack schema.
    struct Schema
    {
        static auto constexpr name   = "Stack";
        static int constexpr version = 1;
    };

    using Parent = Composition;

    /// @brief Create a new stack.
    ///
    /// @param name The name of the stack.
    /// @param source_range The source range of the stack.
    /// @param metadata The metadata for the stack.
    /// @param effects The list of effects for the stack. Note that the
    /// the stack keeps a retainer to each effect.
    /// @param markers The list of markers for the stack. Note that the
    /// the stack keeps a retainer to each marker.
    Stack(
        std::string const&              name         = std::string(),
        std::optional<TimeRange> const& source_range = std::nullopt,
        AnyDictionary const&            metadata     = AnyDictionary(),
        std::vector<Effect*> const&     effects      = std::vector<Effect*>(),
        std::vector<Marker*> const&     markers      = std::vector<Marker*>());

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

    std::vector<Retainer<Composable>> children_in_range(
        TimeRange const& search_range,
        ErrorStatus*     error_status = nullptr) const override;

    std::optional<IMATH_NAMESPACE::Box2d>
    available_image_bounds(ErrorStatus* error_status) const override;

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



    void invalidate_cache() const override;
protected:
    virtual ~Stack();

    std::string composition_kind() const override;

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    mutable std::unordered_map<int, TimeRange> _childRangesCacche;
    mutable std::optional<TimeRange> _availableRangeCache;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
