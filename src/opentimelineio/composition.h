#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/item.h"
#include <set>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class Composition : public Item {
public:
    struct Schema {
        static auto constexpr name = "Composition";
        static int constexpr version = 1;
    };

    using Parent = Item;

    Composition(std::string const& name = std::string(),
                optional<TimeRange> const& source_range = nullopt,
                AnyDictionary const& metadata = AnyDictionary(),
                std::vector<Effect*> const& effects = std::vector<Effect*>(),
                std::vector<Marker*> const& markers = std::vector<Marker*>());

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
        return insert_child(int(_children.size()), child, error_status);
    }

    bool is_parent_of(Composable const* other) const;
    
    virtual std::pair<optional<RationalTime>, optional<RationalTime>>
    handles_of_child(Composable const* child, ErrorStatus* error_status) const;
    
    virtual TimeRange range_of_child_at_index(int index, ErrorStatus* error_status) const;
    virtual TimeRange trimmed_range_of_child_at_index(int index, ErrorStatus* error_status) const;

    // leaving out reference_space argument for now:
    TimeRange range_of_child(Composable const* child, ErrorStatus* error_status) const;
    optional<TimeRange> trimmed_range_of_child(Composable const* child, ErrorStatus* error_status) const;

    optional<TimeRange> trim_child_range(TimeRange child_range) const;

    bool has_child(Composable* child) const;
    
    virtual std::map<Composable*, TimeRange> range_of_all_children(ErrorStatus* error_status) const;

protected:
    virtual ~Composition();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

    int _index_of_child(Composable const* child, ErrorStatus* error_status) const;
    std::vector<Composition*> _path_from_child(Composable const* child, ErrorStatus* error_status) const;
    
private:
    // XXX: python implementation is O(n^2) in number of children
    std::vector<Composable*> _children_at_time(RationalTime, ErrorStatus* error_status) const;

    std::vector<Retainer<Composable>> _children;
    
    // This is for fast lookup only, and varies automatically
    // as _children is mutated.
    std::set<Composable*> _child_set;
};

} }

