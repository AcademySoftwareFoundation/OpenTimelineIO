#ifndef OTIO_TIME_EFFECT_H
#define OTIO_TIME_EFFECT_H

#include "opentimelineio/effect.h"

class TimeEffect : public Effect {
public:
    struct Schema {
        static auto constexpr name = "TimeEffect";
        static int constexpr version = 1;
    };

    using Parent = Effect;

    TimeEffect(std::string const& name = std::string(),
               std::string const& effect_name = std::string(),
               AnyDictionary const& metadata = AnyDictionary());
protected:
    virtual ~TimeEffect();

};

#endif
