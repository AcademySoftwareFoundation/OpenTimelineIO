// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/generatorReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

GeneratorReference::GeneratorReference(
    std::string const&                           name,
    std::string const&                           generator_kind,
    std::optional<TimeRange> const&              available_range,
    AnyDictionary const&                         parameters,
    AnyDictionary const&                         metadata,
    std::optional<IMATH_NAMESPACE::Box2d> const& available_image_bounds)
    : Parent(name, available_range, metadata, available_image_bounds)
    , _generator_kind(generator_kind)
    , _parameters(parameters)
{}

GeneratorReference::~GeneratorReference()
{}

bool
GeneratorReference::read_from(Reader& reader)
{
    return reader.read("generator_kind", &_generator_kind)
           && reader.read("parameters", &_parameters)
           && Parent::read_from(reader);
}

void
GeneratorReference::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("generator_kind", _generator_kind);
    writer.write("parameters", _parameters);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
