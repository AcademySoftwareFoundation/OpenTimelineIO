#include "opentimelineio/marker.h"
#include "opentimelineio/missingReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

Marker::Marker(
    std::string const&   name,
    TimeRange const&     marked_range,
    std::string const&   color,
    AnyDictionary const& metadata)
    : Parent(name, metadata)
    , _color(color)
    , _marked_range(marked_range)
{}

Marker::~Marker()
{}

bool
Marker::read_from(Reader& reader)
{
    return reader.read_if_present("color", &_color) &&
           reader.read("marked_range", &_marked_range) &&
           Parent::read_from(reader);
}

void
Marker::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("color", _color);
    writer.write("marked_range", _marked_range);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
