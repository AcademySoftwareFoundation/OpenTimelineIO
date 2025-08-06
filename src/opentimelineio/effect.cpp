// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/effect.h"
#include "opentimelineio/missingReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

Effect::Effect(
    std::string const&   name,
    std::string const&   effect_name,
    AnyDictionary const& metadata,
    bool enabled)
    : Parent(name, metadata)
    , _effect_name(effect_name)
    , _enabled(enabled)
{}

Effect::~Effect()
{}

bool
Effect::read_from(Reader& reader)
{
    return reader.read("effect_name", &_effect_name)
           && reader.read_if_present("enabled", &_enabled)
           && Parent::read_from(reader);
}

void
Effect::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("effect_name", _effect_name);
    writer.write("enabled", _enabled);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
