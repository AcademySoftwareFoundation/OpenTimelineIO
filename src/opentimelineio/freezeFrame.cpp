// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/freezeFrame.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

FreezeFrame::FreezeFrame(std::string const& name, AnyDictionary const& metadata)
    : Parent(name, "FreezeFrame", 0.0, metadata)
{}

FreezeFrame::~FreezeFrame()
{}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
