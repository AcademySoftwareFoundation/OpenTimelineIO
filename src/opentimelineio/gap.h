// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/item.h"
#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief An empty item within a timeline.
class OPENTIMELINEIO_EXPORT Gap : public Item
{
public:
    /// @brief This struct provides the Gap schema.
    struct Schema
    {
        static auto constexpr name   = "Gap";
        static int constexpr version = 1;
    };

    using Parent = Item;

    /// @brief Create a new gap.
    ///
    /// @param source_range The source range of the gap.
    /// @param name The name of the gap.
    /// @param effects The list of effects for the gap. Note that the
    /// the gap keeps a retainer to each effect.
    /// @param markers The list of markers for the gap. Note that the
    /// the gap keeps a retainer to each marker.
    /// @param metadata The metadata for the gap.
    Gap(TimeRange const&            source_range = TimeRange(),
        std::string const&          name         = std::string(),
        std::vector<Effect*> const& effects      = std::vector<Effect*>(),
        std::vector<Marker*> const& markers      = std::vector<Marker*>(),
        AnyDictionary const&        metadata     = AnyDictionary());

    /// @brief Create a new gap.
    ///
    /// @param duration The duration of the gap.
    /// @param name The name of the gap.
    /// @param effects The list of effects for the gap. Note that the
    /// the gap keeps a retainer to each effect.
    /// @param markers The list of markers for the gap. Note that the
    /// the gap keeps a retainer to each marker.
    /// @param metadata The metadata for the gap.
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
