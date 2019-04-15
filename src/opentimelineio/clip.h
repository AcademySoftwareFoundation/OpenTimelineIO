#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/item.h"
#include "opentimelineio/mediaReference.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class Clip : public Item {
public:
    struct Schema {
        static auto constexpr name = "Clip";
        static int constexpr version = 1;
    };

    using Parent = Item;

    Clip(std::string const& name = std::string(),
         MediaReference* media_reference = nullptr,
         optional<TimeRange> const& source_range = nullopt,
         AnyDictionary const& metadata = AnyDictionary());

    void set_media_reference(MediaReference* media_reference);

    MediaReference* media_reference() const;
    
    virtual TimeRange available_range(ErrorStatus* error_status) const;

protected:
    virtual ~Clip();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    Retainer<MediaReference> _media_reference;
};

} }
