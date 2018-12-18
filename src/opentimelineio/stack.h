#pragma once

#include "opentimelineio/composition.h"

class Stack : public Composition {
public:
    struct Schema {
        static auto constexpr name = "Stack";
        static int constexpr version = 1;
    };

    using Parent = Composition;

    Stack(std::string const& name = std::string(),
          optional<TimeRange> const& source_range = nullopt,
          AnyDictionary const& metadata = AnyDictionary());

    virtual TimeRange range_of_child_at_index(int index, ErrorStatus* error_status) const;
    virtual TimeRange trimmed_range_of_child_at_index(int index, ErrorStatus* error_status) const;
    virtual TimeRange available_range(ErrorStatus* error_status) const;

protected:
    virtual ~Stack();

    virtual std::string const& composition_kind() const;

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:

};
