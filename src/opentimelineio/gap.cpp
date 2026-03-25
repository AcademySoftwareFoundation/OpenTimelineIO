// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/gap.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

Gap::Gap(
    TimeRange const&            source_range,
    std::string const&          name,
    std::vector<Effect*> const& effects,
    std::vector<Marker*> const& markers,
    AnyDictionary const&        metadata)
    : Parent(name, source_range, metadata, effects, markers)
{}

Gap::Gap(
    RationalTime                duration,
    std::string const&          name,
    std::vector<Effect*> const& effects,
    std::vector<Marker*> const& markers,
    AnyDictionary const&        metadata)
    : Parent(
          name,
          TimeRange(RationalTime(0, duration.rate()), duration),
          metadata,
          effects,
          markers)
{}

Gap::~Gap()
{}

bool
Gap::visible() const
{
    return false;
}

bool
Gap::read_from(Reader& reader)
{
    return Parent::read_from(reader);
}

void
Gap::write_to(Writer& writer) const
{
    Parent::write_to(writer);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
