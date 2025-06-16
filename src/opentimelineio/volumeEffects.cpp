#include "volumeEffects.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

bool AudioVolume::read_from(Reader& reader) {
    return reader.read("gain",& _gain)
        && Parent::read_from(reader);
}

void AudioVolume::write_to(Writer &writer) const {
    Parent::write_to(writer);
    writer.write("gain", _gain);
}

bool AudioFade::read_from(Reader& reader) {
    return reader.read("fade_in", &_fade_in)
        && reader.read("start_time", &_start_time)
        && reader.read("duration", &_duration)
        && Parent::read_from(reader);
}

void AudioFade::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("fade_in", _fade_in);
    writer.write("start_time", _start_time);
    writer.write("duration", _duration);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
