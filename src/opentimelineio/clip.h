// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/item.h"
#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Clip : public Item
{
public:
    static char constexpr default_media_key[] = "DEFAULT_MEDIA";

    struct Schema
    {
        static auto constexpr name   = "Clip";
        static int constexpr version = 2;
    };

    using Parent = Item;

    Clip(
        std::string const&              name                       = std::string(),
        MediaReference*                 media_reference            = nullptr,
        std::optional<TimeRange> const& source_range               = std::nullopt,
        AnyDictionary const&            metadata                   = AnyDictionary(),
        std::string const&              active_media_reference_key = default_media_key);

    void            set_media_reference(MediaReference* media_reference);
    MediaReference* media_reference() const noexcept;

    using MediaReferences = std::map<std::string, MediaReference*>;

    MediaReferences media_references() const noexcept;
    void            set_media_references(
                   MediaReferences const& media_references,
                   std::string const&     new_active_key,
                   ErrorStatus*           error_status = nullptr) noexcept;

    std::string active_media_reference_key() const noexcept;
    void        set_active_media_reference_key(
               std::string const& new_active_key,
               ErrorStatus*       error_status = nullptr) noexcept;

    TimeRange
    available_range(ErrorStatus* error_status = nullptr) const override;

    std::optional<IMATH_NAMESPACE::Box2d>
    available_image_bounds(ErrorStatus* error_status) const override;

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

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
