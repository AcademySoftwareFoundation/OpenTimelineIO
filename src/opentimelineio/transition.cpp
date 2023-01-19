// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/transition.h"
#include "opentimelineio/composition.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

Transition::Transition(
    std::string const&   name,
    std::string const&   transition_type,
    RationalTime         in_offset,
    RationalTime         out_offset,
    AnyDictionary const& metadata)
    : Parent(name, metadata)
    , _transition_type(transition_type)
    , _in_offset(in_offset)
    , _out_offset(out_offset)
{}

Transition::~Transition()
{}

bool
Transition::overlapping() const
{
    return true;
}

bool
Transition::read_from(Reader& reader)
{
    return reader.read("in_offset", &_in_offset)
           && reader.read("out_offset", &_out_offset)
           && reader.read("transition_type", &_transition_type)
           && Parent::read_from(reader);
}

void
Transition::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("in_offset", _in_offset);
    writer.write("out_offset", _out_offset);
    writer.write("transition_type", _transition_type);
}

RationalTime
Transition::duration(ErrorStatus* /* error_status */) const
{
    return _in_offset + _out_offset;
}

std::optional<TimeRange>
Transition::range_in_parent(ErrorStatus* error_status) const
{
    if (!parent())
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::NOT_A_CHILD,
                "cannot compute range in parent because item has no parent",
                this);
        }
    }

    return parent()->range_of_child(this, error_status);
}

std::optional<TimeRange>
Transition::trimmed_range_in_parent(ErrorStatus* error_status) const
{
    if (!parent())
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::NOT_A_CHILD,
                "cannot compute trimmed range in parent because item has no parent",
                this);
        }
    }

    return parent()->trimmed_range_of_child(this, error_status);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
