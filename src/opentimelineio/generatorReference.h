// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief A reference to dynamically generated media.
class OTIO_API_TYPE GeneratorReference final : public MediaReference
{
public:
    /// @brief This struct provides the GeneratorReference schema.
    struct Schema
    {
        static auto constexpr name   = "GeneratorReference";
        static int constexpr version = 1;
    };

    using Parent = MediaReference;

    /// @brief Create a new generator reference.
    ///
    /// @param name The name of the generator.
    /// @param generator_kind The kind of generator.
    /// @param available_range The available range of the generator.
    /// @param parameters The parameters used to configure the generator.
    /// @param metadata The metadata for the generator.
    /// @param available_image_bounds The spatial bounds of the generator.
    GeneratorReference(
        std::string const&              name            = std::string(),
        std::string const&              generator_kind  = std::string(),
        std::optional<TimeRange> const& available_range = std::nullopt,
        AnyDictionary const&            parameters      = AnyDictionary(),
        AnyDictionary const&            metadata        = AnyDictionary(),
        std::optional<IMATH_NAMESPACE::Box2d> const& available_image_bounds =
            std::nullopt);

    /// @brief Return the kind of generator.
    std::string generator_kind() const noexcept { return _generator_kind; }

    /// @brief Set the kind of generator.
    void set_generator_kind(std::string const& generator_kind)
    {
        _generator_kind = generator_kind;
    }

    /// @brief Modify the generator parameters.
    AnyDictionary& parameters() noexcept { return _parameters; }

    /// @brief Return the generator parameters.
    AnyDictionary parameters() const noexcept { return _parameters; }

protected:
    virtual ~GeneratorReference();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string   _generator_kind;
    AnyDictionary _parameters;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
