#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/mediaReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class GeneratorReference final : public MediaReference {
public:
    struct Schema {
        static auto constexpr name = "GeneratorReference";
        static int constexpr version = 1;
    };

    using Parent = MediaReference;

    GeneratorReference(std::string const& name = std::string(),
                       std::string const& generator_kind = std::string(),
                       optional<TimeRange> const& available_range = nullopt,
                       AnyDictionary const& parameters = AnyDictionary(),
                       AnyDictionary const& metadata = AnyDictionary());
        
    std::string const& generator_kind() const {
        return _generator_kind;
    }
    
    void set_generator_kind(std::string const& generator_kind) {
        _generator_kind = generator_kind;
    }

    AnyDictionary& parameters() {
        return _parameters;
    }

    AnyDictionary const& parameters() const {
        return _parameters;
    }

protected:
    virtual ~GeneratorReference();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::string _generator_kind;
    AnyDictionary _parameters;
};

} }
