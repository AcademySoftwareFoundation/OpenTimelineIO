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
        AnyDictionary const& metadata     = AnyDictionary());

    std::string color() const noexcept { return _color; }

    void set_color(std::string const& color) { _color = color; }

    TimeRange marked_range() const noexcept { return _marked_range; }

    void set_marked_range(TimeRange const& marked_range) noexcept
    {
        _marked_range = marked_range;
    }

protected:
    virtual ~Marker();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::string _color;
    TimeRange   _marked_range;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
