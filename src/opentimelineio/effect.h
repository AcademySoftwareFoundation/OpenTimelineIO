// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief An effect that can be applied to an item, such as an image or audio filter.
class OPENTIMELINEIO_EXPORT Effect : public SerializableObjectWithMetadata
{
public:
    /// @brief This struct provides the Effect schema.
    struct Schema
    {
        static auto constexpr name   = "Effect";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    /// @brief Create a new effect.
    ///
    /// @param name The name of the effect object.
    /// @param name The name of the effect.
    /// @param metadata The metadata for the clip.
    /// @param enabled Whether the effect is enabled.
    Effect(
        std::string const&   name        = std::string(),
        std::string const&   effect_name = std::string(),
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true);

    /// @brief Return the effect name.
    std::string effect_name() const noexcept { return _effect_name; }

    /// @brief Set the effect name.
    void set_effect_name(std::string const& effect_name)
    {
        _effect_name = effect_name;
    }

    /// @brief Return whether the effect is enabed.
    bool enabled() const { return _enabled; };

    /// @brief Set whether the effect is enabled.
    void set_enabled(bool enabled) { _enabled = enabled; }  

protected:
    virtual ~Effect();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string _effect_name;
    bool        _enabled;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
