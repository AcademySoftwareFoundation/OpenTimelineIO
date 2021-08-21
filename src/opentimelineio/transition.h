#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/composable.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

class Transition : public Composable {
public:
    struct Type {
        static auto constexpr SMPTE_Dissolve = "SMPTE_Dissolve";
        static auto constexpr Custom = "Custom_Transition";
    };
    
    struct Schema {
        static auto constexpr name = "Transition";
        static int constexpr version = 1;
    };

    using Parent = Composable;

    Transition(std::string const& name = std::string(),
               std::string const& transition_type = std::string(),
               RationalTime in_offset = RationalTime(),
               RationalTime out_offset = RationalTime(),
               AnyDictionary const& metadata = AnyDictionary());

    virtual bool overlapping() const;

    std::string transition_type() const {
        return _transition_type;
    }
    
    void set_transition_type(std::string const& transition_type) {
        _transition_type = transition_type;
    }

    RationalTime in_offset() const {
        return _in_offset;
    }
    
    void set_in_offset(RationalTime in_offset) {
        _in_offset = in_offset;
    }

    RationalTime out_offset() const {
        return _out_offset;
    }
    
    void set_out_offset(RationalTime out_offset) {
        _out_offset = out_offset;
    }

    // XX is this virtual?
    virtual RationalTime duration(ErrorStatus* error_status) const;

    optional<TimeRange> range_in_parent(ErrorStatus* error_status) const;

    optional<TimeRange> trimmed_range_in_parent(ErrorStatus* error_status) const;
    
protected:
    virtual ~Transition();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::string _transition_type;
    RationalTime _in_offset, _out_offset;
};

} }
