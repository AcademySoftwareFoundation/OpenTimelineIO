#include "opentimelineio/timeEffect.h"

TimeEffect::TimeEffect(std::string const& name,
                       std::string const& effect_name,
                       AnyDictionary const& metadata)
    : Parent(name, effect_name, metadata) {
}

TimeEffect::~TimeEffect() {
}
