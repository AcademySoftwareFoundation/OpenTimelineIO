#ifndef OTIO_MARKER_H
#define OTIO_MARKER_H

#include "serializableObjectWithMetadata.h"

class Marker : public SerializableObjectWithMetadata {
public:
    struct Color {
        static auto constexpr pink = "pink";
        static auto constexpr red = "red";
        static auto constexpr orange = "orange";
        static auto constexpr yellow = "yellow";
        static auto constexpr green = "green";
        static auto constexpr cyan = "cyan";
        static auto constexpr blue = "blue";
        static auto constexpr purple = "purple";
        static auto constexpr magenta = "magenta";
        static auto constexpr black = "black";
        static auto constexpr white = "white";
    };
    
    struct Schema {
        static auto constexpr name = "Marker";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    Marker(std::string const& name = std::string(),
           TimeRange const& marked_range = TimeRange(),
           std::string const& color = Color::green,
           AnyDictionary const& metadata = AnyDictionary());

    std::string const& color() const;
    void set_color(std::string const& color);

    TimeRange const& marked_range() const;
    void set_marked_range(TimeRange const& marked_range);

protected:
    virtual ~Marker();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::string _color;
    TimeRange _marked_range;
};

#endif
