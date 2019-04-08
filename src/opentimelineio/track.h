#ifndef OTIO_TRACK_H
#define OTIO_TRACK_H

#include "opentimelineio/composition.h"

class Track : public Composition {
public:
    struct Kind {
        static auto constexpr video = "Video";
        static auto constexpr audio = "Audio";
    };
        
    struct Schema {
        static auto constexpr name = "Track";
        static int constexpr version = 1;
    };

    using Parent = Composition;

    Track(std::string const& name = std::string(),
          optional<TimeRange> const& source_range = nullopt,
          std::string const& = Kind::video,
          AnyDictionary const& metadata = AnyDictionary());

    std::string const& kind() const {
        return _kind;
    }
    
    void set_kind(std::string const& kind) {
        _kind = kind;
    }


protected:
    virtual ~Track();
    virtual std::string const& composition_kind() const;

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::string _kind;
};

#endif
