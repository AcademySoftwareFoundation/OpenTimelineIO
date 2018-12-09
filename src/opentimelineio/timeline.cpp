#include "opentimelineio/timeline.h"

Timeline::Timeline(std::string const& name,
                   RationalTime global_start_time,
                   AnyDictionary const& metadata)
    : SerializableObjectWithMetadata(name, metadata),
      _global_start_time(global_start_time),
      _tracks(new Stack("tracks")) {
}

Timeline::~Timeline() {
}

bool Timeline::read_from(Reader& reader) {
    return reader.read("tracks", &_tracks) &&
        // reader.read("global_start_time", &_global_start_time) &&
        Parent::read_from(reader);
}

void Timeline::write_to(Writer& writer) const {
    Parent::write_to(writer);
    // writer.write("global_start_time", _global_start_time);
    writer.write("tracks", _tracks);
}
