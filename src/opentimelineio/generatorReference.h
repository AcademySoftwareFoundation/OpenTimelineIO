// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/mediaReference.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class GeneratorReference final : public MediaReference
{
public:
    struct Schema
    {
        static auto constexpr name   = "GeneratorReference";
        static int constexpr version = 1;
    };

    using Parent = MediaReference;

    GeneratorReference(
        std::string const&                 name                   = std::string(),
        std::string const&                 generator_kind         = std::string(),
        std::optional<TimeRange> const&    available_range        = std::nullopt,
        AnyDictionary const&               parameters             = AnyDictionary(),
        AnyDictionary const&               metadata               = AnyDictionary(),
        std::optional<Imath::Box2d> const& available_image_bounds = std::nullopt);

    std::string generator_kind() const noexcept { return _generator_kind; }

    void set_generator_kind(std::string const& generator_kind)
    {
        _generator_kind = generator_kind;
    }

    AnyDictionary& parameters() noexcept { return _parameters; }

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
