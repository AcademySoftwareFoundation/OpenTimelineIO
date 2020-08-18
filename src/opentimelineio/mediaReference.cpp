#include "opentimelineio/mediaReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

MediaReference::MediaReference(std::string const& name,
                               optional<TimeRange> const& available_range,
                               AnyDictionary const& metadata,
                               optional<Box> const& bounds)
    : Parent(name, metadata),
      _available_range(available_range),
      _bounds(bounds) {
}

MediaReference::~MediaReference() {
}


bool MediaReference::is_missing_reference() const {
    return false;
}

bool MediaReference::read_from(Reader& reader) {
    return reader.read_if_present("available_range", &_available_range) &&
           reader.read_if_present("bounds", &_bounds) &&
        Parent::read_from(reader);
}

void MediaReference::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("available_range", _available_range);
    writer.write("bounds", _bounds);
}

} }
