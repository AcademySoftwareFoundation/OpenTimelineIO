#include "opentimelineio/freezeFrame.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
FreezeFrame::FreezeFrame(std::string const& name,
                         AnyDictionary const& metadata)
    : Parent(name, "FreezeFrame", metadata) {
}

FreezeFrame::~FreezeFrame() {
}

} }
