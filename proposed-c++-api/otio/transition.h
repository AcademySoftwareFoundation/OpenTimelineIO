#ifndef OTIO_TRANSITION_H
#define OTIO_TRANSITION_H

#include "composable.h"
    
class Transition : public Composable {
public:
    struct Type {
        static auto constexpr SMPTE_Dissolve = "SMPTE_Dissolve";
        static auto constexpr custom = "custom";
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

protected:
    virtual ~Transition();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    RationalTime _in_offset, _out_offset;
};

#endif
