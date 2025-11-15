// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/timeEffect.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

TimeEffect::TimeEffect(
    std::string const&   name,
    std::string const&   effect_name,
    AnyDictionary const& metadata)
    : Parent(name, effect_name, metadata)
{}

TimeEffect::~TimeEffect()
{}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
