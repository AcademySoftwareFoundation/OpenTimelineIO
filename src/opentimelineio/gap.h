// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/item.h"
#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Gap : public Item
{
public:
    struct Schema
    {
        static auto constexpr name   = "Gap";
        static int constexpr version = 1;
    };

    using Parent = Item;

    Gap(TimeRange const&            source_range = TimeRange(),
        std::string const&          name         = std::string(),
        std::vector<Effect*> const& effects      = std::vector<Effect*>(),
        std::vector<Marker*> const& markers      = std::vector<Marker*>(),
        AnyDictionary const&        metadata     = AnyDictionary());

    Gap(RationalTime                duration,
        std::string const&          name     = std::string(),
        std::vector<Effect*> const& effects  = std::vector<Effect*>(),
        std::vector<Marker*> const& markers  = std::vector<Marker*>(),
        AnyDictionary const&        metadata = AnyDictionary());

    bool visible() const override;

protected:
    virtual ~Gap();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
