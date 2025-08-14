// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/composable.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {
/// @brief Represents a transition between the two adjacent items in a Track.
///
/// For example, a cross dissolve or wipe.
class OPENTIMELINEIO_EXPORT Transition : public Composable
{
public:
    /// @brief This struct provides base set of transitions.
    struct Type
    {
        static auto constexpr SMPTE_Dissolve = "SMPTE_Dissolve";
        static auto constexpr Custom         = "Custom_Transition";
    };

    /// @brief This struct provides the Transition schema.
    struct Schema
    {
        static auto constexpr name   = "Transition";
        static int constexpr version = 1;
    };

    using Parent = Composable;

    /// @brief Create a new transition.
    ///
    /// @param name The transition name.
    /// @param transition_type The transition type.
    /// @param in_offset The in time offset.
    /// @param out_offset The out time offset.
    /// @param metadata The metadata for the transition.
    Transition(
        std::string const&   name            = std::string(),
        std::string const&   transition_type = std::string(),
        RationalTime         in_offset       = RationalTime(),
        RationalTime         out_offset      = RationalTime(),
        AnyDictionary const& metadata        = AnyDictionary());

    bool overlapping() const override;

    /// @brief Return the transition type.
    std::string transition_type() const noexcept { return _transition_type; }

    /// @brief Set the transition type.
    void set_transition_type(std::string const& transition_type)
    {
        _transition_type = transition_type;
    }

    /// @brief Return the transition in time offset.
    RationalTime in_offset() const noexcept { return _in_offset; }

    /// @brief Set the transition in time offset.
    void set_in_offset(RationalTime const& in_offset) noexcept
    {
        _in_offset = in_offset;
    }

    /// @brief Return the transition out time offset.
    RationalTime out_offset() const noexcept { return _out_offset; }

    /// @brief Set the transition out time offset.
    void set_out_offset(RationalTime const& out_offset) noexcept
    {
        _out_offset = out_offset;
    }

    RationalTime duration(ErrorStatus* error_status = nullptr) const override;

    /// @brief Return the range in the parent's time.
    std::optional<TimeRange>
    range_in_parent(ErrorStatus* error_status = nullptr) const;

    /// @brief Return the range trimmed in the parent's time.
    std::optional<TimeRange>
    trimmed_range_in_parent(ErrorStatus* error_status = nullptr) const;

protected:
    virtual ~Transition();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string  _transition_type;
    RationalTime _in_offset, _out_offset;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
