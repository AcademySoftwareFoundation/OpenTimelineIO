#include "opentimelineio/timeline.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
Timeline::Timeline(std::string const& name,
                   optional<RationalTime> global_start_time,
                   AnyDictionary const& metadata)
    : SerializableObjectWithMetadata(name, metadata),
      _global_start_time(global_start_time),
      _tracks(new Stack("tracks")) {
}

Timeline::~Timeline() {
}

bool Timeline::read_from(Reader& reader) {
    return reader.read("tracks", &_tracks) &&
        reader.read_if_present("global_start_time", &_global_start_time) &&
        Parent::read_from(reader);
}

void Timeline::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("global_start_time", _global_start_time);
    writer.write("tracks", _tracks);
}

std::vector<Track*> Timeline::video_tracks() const {
    std::vector<Track*> result;
    for (auto c: _tracks.value->children()) {
        if (Track* t = dynamic_cast<Track*>(c.value)) {
            if (t->kind() == Track::Kind::video) {
                result.push_back(t);
            }
        }
    }
    return result;
}

std::vector<Track*> Timeline::audio_tracks() const {
    std::vector<Track*> result;
    for (auto c: _tracks.value->children()) {
        if (Track* t = dynamic_cast<Track*>(c.value)) {
            if (t->kind() == Track::Kind::audio) {
                result.push_back(t);
            }
        }
    }
    return result;
}

} }
