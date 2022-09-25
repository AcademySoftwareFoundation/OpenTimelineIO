// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/effect.h"
#include "opentimelineio/missingReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

Effect::Effect(
    std::string const&   name,
    std::string const&   effect_name,
    AnyDictionary const& metadata)
    : Parent(name, metadata)
    , _effect_name(effect_name)
{}

Effect::~Effect()
{}

bool
Effect::read_from(Reader& reader)
{
    return reader.read("effect_name", &_effect_name)
           && Parent::read_from(reader);
}

void
Effect::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("effect_name", _effect_name);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
