#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/mediaReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class MissingReference final : public MediaReference {
public:
    struct Schema {
        static auto constexpr name = "MissingReference";
        static int constexpr version = 1;
    };

    using Parent = MediaReference;

    MissingReference(std::string const& name = std::string(),
                     optional<TimeRange> const& available_range = nullopt,
                     AnyDictionary const& metadata = AnyDictionary());

    virtual bool is_missing_reference() const;

protected:
    virtual ~MissingReference();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;
};

} }
