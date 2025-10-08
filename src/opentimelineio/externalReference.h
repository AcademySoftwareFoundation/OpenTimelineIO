// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief A reference to a media file.
class OTIO_API_TYPE ExternalReference final : public MediaReference
{
public:
    /// @brief This struct provides the ExternalReference schema.
    struct Schema
    {
        static auto constexpr name   = "ExternalReference";
        static int constexpr version = 1;
    };

    using Parent = MediaReference;

    /// @brief Create a new external reference.
    ///
    /// @param target_url The URL to the media.
    /// @param available_range The available range of the media.
    /// @param metadata The metadata for the media.
    /// @param available_image_bounds The spatial bounds of the media.
    OTIO_API ExternalReference(
        std::string const&              target_url      = std::string(),
        std::optional<TimeRange> const& available_range = std::nullopt,
        AnyDictionary const&            metadata        = AnyDictionary(),
        std::optional<IMATH_NAMESPACE::Box2d> const& available_image_bounds =
            std::nullopt);

    /// @brief Return the media file URL.
    std::string target_url() const noexcept { return _target_url; }

    /// @brief Set the media file URL.
    void set_target_url(std::string const& target_url)
    {
        _target_url = target_url;
    }

protected:
    virtual ~ExternalReference();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string _target_url;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
