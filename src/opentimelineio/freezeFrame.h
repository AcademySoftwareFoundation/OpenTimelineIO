#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/linearTimeWarp.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class FreezeFrame : public LinearTimeWarp {
public:
    struct Schema {
        static auto constexpr name = "FreezeFrame";
        static int constexpr version = 1;
    };

    using Parent = LinearTimeWarp;

    FreezeFrame(std::string const& name = std::string(),
                AnyDictionary const& metadata = AnyDictionary());

protected:
    virtual ~FreezeFrame();

private:

};

} }
