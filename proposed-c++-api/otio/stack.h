#ifndef OTIO_STACK_H
#define OTIO_STACK_H

#include "composition.h"

class Stack : public Composition {
public:
    struct Schema {
        static auto constexpr name = "Clip";
        static int constexpr version = 1;
    };

    using Parent = Composition;

    Stack(std::string const& name = std::string(),
          optional<TimeRange> const& source_range = nullopt,
          AnyDictionary const& metadata = AnyDictionary());

protected:
    virtual ~Stack();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:

};

#endif
