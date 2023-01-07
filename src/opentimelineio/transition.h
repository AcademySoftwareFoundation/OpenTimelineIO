// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/composable.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Transition : public Composable
{
public:
    struct Type
    {
        static auto constexpr SMPTE_Dissolve = "SMPTE_Dissolve";
        static auto constexpr Custom         = "Custom_Transition";
    };

    struct Schema
    {
        static auto constexpr name   = "Transition";
        static int constexpr version = 1;
    };

    using Parent = Composable;

    Transition(
        std::string const&   name            = std::string(),
        std::string const&   transition_type = std::string(),
        RationalTime         in_offset       = RationalTime(),
        RationalTime         out_offset      = RationalTime(),
        AnyDictionary const& metadata        = AnyDictionary());

    virtual bool overlapping() const;

    std::string transition_type() const noexcept { return _transition_type; }

    void set_transition_type(std::string const& transition_type)
    {
        _transition_type = transition_type;
    }

    RationalTime in_offset() const noexcept { return _in_offset; }

    void set_in_offset(RationalTime const& in_offset) noexcept
    {
        _in_offset = in_offset;
    }

    RationalTime out_offset() const noexcept { return _out_offset; }

    void set_out_offset(RationalTime const& out_offset) noexcept
    {
        _out_offset = out_offset;
    }

    virtual RationalTime duration(ErrorStatus* error_status = nullptr) const override;

    optional<TimeRange>
    range_in_parent(ErrorStatus* error_status = nullptr) const;

    optional<TimeRange>
    trimmed_range_in_parent(ErrorStatus* error_status = nullptr) const;

protected:
    virtual ~Transition();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::string  _transition_type;
    RationalTime _in_offset, _out_offset;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
