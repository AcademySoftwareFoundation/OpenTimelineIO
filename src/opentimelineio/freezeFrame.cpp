#include "opentimelineio/freezeFrame.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
FreezeFrame::FreezeFrame(std::string const& name,
                         RationalTime duration,
                         AnyDictionary const& metadata)
    : Parent(name, "FreezeFrame", metadata),
      _duration(duration) {
}

FreezeFrame::~FreezeFrame() {
}

bool FreezeFrame::read_from(Reader& reader) {
    return reader.read("duration", &_duration) &&
        Parent::read_from(reader);
}

void FreezeFrame::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("duration", _duration);
}

} }
