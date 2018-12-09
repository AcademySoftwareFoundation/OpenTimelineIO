#include "opentimelineio/clip.h"
#include "opentimelineio/missingReference.h"

Clip::Clip(std::string const& name,
           MediaReference* media_reference,
           optional<TimeRange> const& source_range,
           AnyDictionary const& metadata)
    : Parent(name, source_range, metadata)
{
    set_media_reference(media_reference ? media_reference : new MissingReference);
}

Clip::~Clip() {
}

MediaReference* Clip::media_reference() const {
    return _media_reference.value;
}


void  Clip::set_media_reference(MediaReference* media_reference) {
    _media_reference = media_reference;
}


bool Clip::read_from(Reader& reader) {
    return reader.read("media_reference", &_media_reference) &&
           Parent::read_from(reader);
}

void Clip::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("media_reference", _media_reference);
}
