#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/track.h"
#include "opentimelineio/stack.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

class Clip;

class Timeline : public SerializableObjectWithMetadata {
public:
    struct Schema {
        static auto constexpr name = "Timeline";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    Timeline(std::string const& name = std::string(),
             optional<RationalTime> global_start_time = nullopt,
             AnyDictionary const& metadata = AnyDictionary());

    Stack* tracks() const {
        return _tracks;
    }

    /*
    Stack* tracks() {
        return _tracks;
    }*/
    

    void set_tracks(Stack* stack) {
        _tracks = stack;
    }
    
    optional<RationalTime> const& global_start_time() const {
        return _global_start_time;
    }
    
    void set_global_start_time(optional<RationalTime> const& global_start_time) {
        _global_start_time = global_start_time;
    }

    RationalTime duration(ErrorStatus* error_status) const {
        return _tracks.value->duration(error_status);
    }
    
    TimeRange range_of_child(Composable const* child, ErrorStatus* error_status) const {
        return _tracks.value->range_of_child(child, error_status);
    }

    std::vector<Track*> audio_tracks() const;
    std::vector<Track*> video_tracks() const;

    // Return a vector of clips.
    //
    // An optional search_range may be provided to limit the search.
    std::vector<Retainer<Clip> > each_clip(
        ErrorStatus* error_status,
        optional<TimeRange> const& search_range = nullopt) const;

    // Return a vector of all objects that match the given template type.
    //
    // An optional search_time may be provided to limit the search.
    template<typename T = Composable>
    std::vector<Retainer<T>> each_child(
        ErrorStatus* error_status,
        optional<TimeRange> search_range = nullopt) const;
    
protected:
    virtual ~Timeline();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    optional<RationalTime> _global_start_time;
    Retainer<Stack> _tracks;
};

template<typename T>
inline std::vector<SerializableObject::Retainer<T>> Timeline::each_child(
    ErrorStatus* error_status,
    optional<TimeRange> search_range) const
{
    return _tracks.value->each_child<T>(error_status, search_range);
}

} }
