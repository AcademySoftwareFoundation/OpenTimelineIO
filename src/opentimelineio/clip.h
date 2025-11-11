// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/item.h"
#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

/// @brief A clip is a segment of editable media (usually audio or video).
///
/// Contains a MediaReference and a trim on that media reference.
class OTIO_API_TYPE Clip : public Item
{
public:
    /// @brief The default media within a clip.
    static char constexpr default_media_key[] = "DEFAULT_MEDIA";

    /// @brief This struct provides the Clip schema.
    struct Schema
    {
        static auto constexpr name   = "Clip";
        static int constexpr version = 2;
    };

    using Parent = Item;

    /// @brief Create a new clip.
    ///
    /// @param name The name of the clip.
    /// @param media_reference The media reference for the clip. Note
    /// that the Clip keeps a Retainer to the media reference.
    /// @param source_range The source range of the clip.
    /// @param metadata The metadata for the clip.
    /// @param effects The list of effects for the clip. Note that the
    /// the clip keeps a retainer to each effect.
    /// @param markers The list of markers for the clip. Note that the
    /// the clip keeps a retainer to each marker.
    /// @param active_media_reference_key The active media reference.
    OTIO_API Clip(
        std::string const&              name            = std::string(),
        MediaReference*                 media_reference = nullptr,
        std::optional<TimeRange> const& source_range    = std::nullopt,
        AnyDictionary const&            metadata        = AnyDictionary(),
        std::vector<Effect*> const&     effects       = std::vector<Effect*>(),
        std::vector<Marker*> const&     markers       = std::vector<Marker*>(),
        std::string const& active_media_reference_key = default_media_key,
        std::optional<Color> const& color             = std::nullopt);

    /// @name Media References
    ///@{

    /// @brief Set the media reference. Note that the Clip keeps a Retainer to
    /// the media reference.
    OTIO_API void set_media_reference(MediaReference* media_reference);

    /// @brief Return the media reference.
    OTIO_API MediaReference* media_reference() const noexcept;

    using MediaReferences = std::map<std::string, MediaReference*>;

    /// @brief Return the list of media references.
    OTIO_API MediaReferences media_references() const noexcept;

    /// @brief Set the list of media references. Note that the Clip keeps a
    /// Retainer to each media reference.
    OTIO_API void set_media_references(
        MediaReferences const& media_references,
        std::string const&     new_active_key,
        ErrorStatus*           error_status = nullptr) noexcept;

    /// @brief Return the active media reference.
    OTIO_API std::string active_media_reference_key() const noexcept;

    /// @brief Set the active media reference.
    OTIO_API void set_active_media_reference_key(
        std::string const& new_active_key,
        ErrorStatus*       error_status = nullptr) noexcept;

    ///@}

    OTIO_API TimeRange
    available_range(ErrorStatus* error_status = nullptr) const override;

    OTIO_API std::optional<IMATH_NAMESPACE::Box2d>
    available_image_bounds(ErrorStatus* error_status = nullptr) const override;

protected:
    virtual ~Clip();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    template <typename MediaRefMap>
    bool check_for_valid_media_reference_key(
        std::string const& caller,
        std::string const& key,
        MediaRefMap const& media_references,
        ErrorStatus*       error_status);

private:
    std::map<std::string, Retainer<MediaReference>> _media_references;
    std::string                                     _active_media_reference_key;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
