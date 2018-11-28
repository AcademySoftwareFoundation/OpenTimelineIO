#ifndef OTIO_FREEZE_FRAME_H
#define OTIO_FREEZE_FRAME_H

#include "linearTimeWarp.h"

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

#endif
