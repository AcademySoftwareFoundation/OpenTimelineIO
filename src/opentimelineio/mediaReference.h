#ifndef OTIO_MEDIA_REFERENCE_H
#define OTIO_MEDIA_REFERENCE_H

#include "opentimelineio/serializableObjectWithMetadata.h"

class MediaReference : public SerializableObjectWithMetadata {
public:
    struct Schema {
        static auto constexpr name = "MediaReference";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    MediaReference(std::string const& name = std::string(),
                   optional<TimeRange> const& available_range = nullopt,
                   AnyDictionary const& metadata = AnyDictionary());

    optional<TimeRange> const& available_range () const {
        return _available_range;
    }

    void set_available_range(optional<TimeRange> const& available_range) {
        _available_range = available_range;
    }

    virtual bool is_missing_reference() const;
    
protected:
    virtual ~MediaReference();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    optional<TimeRange> _available_range;
};

#endif
