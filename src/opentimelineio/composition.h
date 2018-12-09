#ifndef OTIO_COMPOSITION_H
#define OTIO_COMPOSITION_H

#include "opentimelineio/item.h"

class Composition : public Item {
public:
    struct Schema {
        static auto constexpr name = "Composition";
        static int constexpr version = 1;
    };

    using Parent = Item;

    Composition(std::string const& name = std::string(),
                optional<TimeRange> const& source_range = nullopt,
                AnyDictionary const& metadata = AnyDictionary());

    virtual std::string const& composition_kind() const;

    std::vector<Retainer<Composable>> const& children() const {
        return _children;
    }

    void clear_children();

    bool set_children(std::vector<Composable*> const& children, ErrorStatus* error_status);
    
    bool insert_child(int index, Composable* child, ErrorStatus* error_status);

    bool set_child(int index, Composable* child, ErrorStatus* error_status);

    bool remove_child(int index, ErrorStatus* error_status);

    bool append_child(Composable* child, ErrorStatus* error_status) {
        return insert_child(_children.size(), child, error_status);
    }

    bool is_parent_of(Composable const* other) const;
    
    virtual std::pair<optional<RationalTime>, optional<RationalTime>>
    handles_of_child(Composable const* child) const;

protected:
    virtual ~Composition();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::vector<Retainer<Composable>> _children;
};

#endif
