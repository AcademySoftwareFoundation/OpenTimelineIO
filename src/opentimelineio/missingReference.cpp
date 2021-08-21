#include "opentimelineio/missingReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
MissingReference::MissingReference(std::string const& name,
                                   optional<TimeRange> const& available_range,
                                   AnyDictionary const& metadata)
    : Parent(name, available_range, metadata) {
}

MissingReference::~MissingReference() {
}

bool MissingReference::is_missing_reference() const {
    return true;
}

bool MissingReference::read_from(Reader& reader) {
    return Parent::read_from(reader);
}

void MissingReference::write_to(Writer& writer) const {
    Parent::write_to(writer);
}

} }
