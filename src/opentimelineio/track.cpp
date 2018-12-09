#include "opentimelineio/track.h"

Track::Track(std::string const& name,
             optional<TimeRange> const& source_range,
             std::string const& kind,
             AnyDictionary const& metadata)
    : Parent( name, source_range, metadata),
      _kind(kind) {
}

Track::~Track() {
}

std::string const& Track::composition_kind() const {
    static std::string kind = "Track";
    return kind;
}

bool Track::read_from(Reader& reader) {
    return reader.read("kind", &_kind) &&
        Parent::read_from(reader);
}

void Track::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("kind", _kind);
}
