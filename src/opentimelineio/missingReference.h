// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief Represents media for which a concrete reference is missing.
///
/// Note that a missing reference may have useful metadata, even if the
/// location of the media is not known.
class OTIO_API_TYPE MissingReference final : public MediaReference
{
public:
    /// @brief This struct provides the MissingReference schema.
    struct Schema
    {
        static auto constexpr name   = "MissingReference";
        static int constexpr version = 1;
    };

    using Parent = MediaReference;

    /// @brief Create a new missing reference.
    ///
    /// @param name The name of the missing reference.
    /// @param available_range The available range of the missing reference.
    /// @param metadata The metadata for the missing reference.
    /// @param available_image_bounds The spatial bounds for the missing reference.
    OTIO_API MissingReference(
        std::string const&              name            = std::string(),
        std::optional<TimeRange> const& available_range = std::nullopt,
        AnyDictionary const&            metadata        = AnyDictionary(),
        std::optional<IMATH_NAMESPACE::Box2d> const& available_image_bounds =
            std::nullopt);

    bool is_missing_reference() const override;

protected:
    virtual ~MissingReference();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
