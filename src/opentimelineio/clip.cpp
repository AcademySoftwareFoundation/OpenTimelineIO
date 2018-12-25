#include "opentimelineio/clip.h"
#include "opentimelineio/missingReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
Clip::Clip(std::string const& name,
           MediaReference* media_reference,
           optional<TimeRange> const& source_range,
           AnyDictionary const& metadata)
    : Parent {name, source_range, metadata} {
    set_media_reference(media_reference);
}

Clip::~Clip() {
}

MediaReference* Clip::media_reference() const {
    return _media_reference.value;
}


void  Clip::set_media_reference(MediaReference* media_reference) {
    _media_reference = media_reference ? media_reference : new MissingReference;
}


bool Clip::read_from(Reader& reader) {
    return reader.read("media_reference", &_media_reference) &&
           Parent::read_from(reader);
}

void Clip::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("media_reference", _media_reference);
}

TimeRange Clip::available_range(ErrorStatus* error_status) const {
    if (!_media_reference) {
        *error_status = ErrorStatus(ErrorStatus::CANNOT_COMPUTE_AVAILABLE_RANGE,
                                    "No media reference set on clip", this);
        return TimeRange();
    }
    
    if (!_media_reference.value->available_range()) {
        *error_status = ErrorStatus(ErrorStatus::CANNOT_COMPUTE_AVAILABLE_RANGE,
                                    "No available_range set on media reference on clip", this);
        return TimeRange();
    }
    
    return *_media_reference.value->available_range();
}

} }
