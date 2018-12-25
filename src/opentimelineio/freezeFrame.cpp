#include "opentimelineio/freezeFrame.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
FreezeFrame::FreezeFrame(std::string const& name,
                         AnyDictionary const& metadata)
    : Parent(name, "FreezeFrame", 0.0, metadata) {
}

FreezeFrame::~FreezeFrame() {
}

} }
