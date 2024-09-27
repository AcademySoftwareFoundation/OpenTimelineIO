// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Effect : public SerializableObjectWithMetadata
{
public:
    struct Schema
    {
        static auto constexpr name   = "Effect";
        static int constexpr version = 2;
    };

    using Parent = SerializableObjectWithMetadata;

    Effect(
        std::string const&   name        = std::string(),
        std::string const&   effect_name = std::string(),
        AnyDictionary const& metadata    = AnyDictionary(),
        bool                 enabled     = true);

    std::string effect_name() const noexcept { return _effect_name; }

    void set_effect_name(std::string const& effect_name)
    {
        _effect_name = effect_name;
    }

    bool enabled() const { return _enabled; };

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
