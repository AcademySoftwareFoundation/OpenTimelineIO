#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/timeEffect.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class FreezeFrame : public TimeEffect {
public:
    struct Schema {
        static auto constexpr name = "FreezeFrame";
        static int constexpr version = 1;
    };

    using Parent = TimeEffect;

    FreezeFrame(std::string const& name = std::string(),
                AnyDictionary const& metadata = AnyDictionary());

protected:
    virtual ~FreezeFrame();

private:
};

} }
