#ifndef OTIO_TIMELINE_H
#define OTIO_TIMELINE_H

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/track.h"
#include "opentimelineio/stack.h"

class Timeline : public SerializableObjectWithMetadata {
public:
    struct Schema {
        static auto constexpr name = "Timeline";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    Timeline(std::string const& name = std::string(),
             RationalTime global_start_time = RationalTime(0, 24),
             AnyDictionary const& metadata = AnyDictionary());

    Stack const* tracks() const {
        return _tracks;
    }

    Stack* tracks() {
        return _tracks;
    }

    RationalTime global_start_time() const {
        return _global_start_time;
    }
    
    void set_global_start_time(RationalTime global_start_time) {
        _global_start_time = global_start_time;
    }

    RationalTime duration(ErrorStatus* error_status) const {
        return _tracks.value->duration(error_status);
    }
    
    TimeRange range_of_child(Composable const* child, ErrorStatus* error_status) const {
        return _tracks.value->range_of_child(child, error_status);
    }

    std::vector<Composable*> audio_tracks() const;
    std::vector<Composable*> video_tracks() const;
    
protected:
    virtual ~Timeline();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    RationalTime _global_start_time;
    Retainer<Stack> _tracks;
};

#endif
