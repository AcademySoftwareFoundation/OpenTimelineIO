// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Marker : public SerializableObjectWithMetadata
{
public:
    struct Color
    {
        static auto constexpr pink    = "PINK";
        static auto constexpr red     = "RED";
        static auto constexpr orange  = "ORANGE";
        static auto constexpr yellow  = "YELLOW";
        static auto constexpr green   = "GREEN";
        static auto constexpr cyan    = "CYAN";
        static auto constexpr blue    = "BLUE";
        static auto constexpr purple  = "PURPLE";
        static auto constexpr magenta = "MAGENTA";
        static auto constexpr black   = "BLACK";
        static auto constexpr white   = "WHITE";
    };

    struct Schema
    {
        static auto constexpr name   = "Marker";
        static int constexpr version = 2;
    };

    using Parent = SerializableObjectWithMetadata;

    Marker(
        std::string const&   name         = std::string(),
        TimeRange const&     marked_range = TimeRange(),
        std::string const&   color        = Color::green,
        AnyDictionary const& metadata     = AnyDictionary(),
        std::string const&   comment      = std::string());

    std::string color() const noexcept { return _color; }

    void set_color(std::string const& color) { _color = color; }

    TimeRange marked_range() const noexcept { return _marked_range; }

    void set_marked_range(TimeRange const& marked_range) noexcept
    {
        _marked_range = marked_range;
    }

    std::string comment() const noexcept { return _comment; }

    void set_comment(std::string const& comment) { _comment = comment; }

protected:
    virtual ~Marker();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string _color;
    TimeRange   _marked_range;
    std::string _comment;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
