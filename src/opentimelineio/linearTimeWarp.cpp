// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/linearTimeWarp.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

LinearTimeWarp::LinearTimeWarp(
    std::string const&   name,
    std::string const&   effect_name,
    double               time_scalar,
    AnyDictionary const& metadata)
    : Parent(name, effect_name, metadata)
    , _time_scalar(time_scalar)
{}

LinearTimeWarp::~LinearTimeWarp()
{}

bool
LinearTimeWarp::read_from(Reader& reader)
{
    return reader.read("time_scalar", &_time_scalar)
           && Parent::read_from(reader);
}

void
LinearTimeWarp::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("time_scalar", _time_scalar);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
