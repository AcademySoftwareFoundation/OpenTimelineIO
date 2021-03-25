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

    template<typename T = Composable>
    std::vector<Retainer<T>> each_child(
        ErrorStatus* error_status,
        optional<TimeRange> search_range = nullopt,
        bool shallow_search = false) const;

protected:
    virtual ~Composition();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

    int _index_of_child(Composable const* child, ErrorStatus* error_status) const;
    std::vector<Composition*> _path_from_child(Composable const* child, ErrorStatus* error_status) const;
    
private:
    // XXX: python implementation is O(n^2) in number of children
    std::vector<Composable*> _children_at_time(RationalTime, ErrorStatus* error_status) const;

    size_t _bisect_right(
        RationalTime const& tgt,
        std::function<RationalTime(Composable*)> const& key_func,
        ErrorStatus* error_status,
        optional<size_t> lower_search_bound = optional<size_t>(0),
        optional<size_t> upper_search_bound = nullopt) const;
    size_t _bisect_left(
        RationalTime const& tgt,
        std::function<RationalTime(Composable*)> const& key_func,
        ErrorStatus* error_status,
        optional<size_t> lower_search_bound = optional<size_t>(0),
        optional<size_t> upper_search_bound = nullopt) const;

    std::vector<Retainer<Composable>> _children;
    
    // This is for fast lookup only, and varies automatically
    // as _children is mutated.
    std::set<Composable*> _child_set;
};

template<typename T>
inline std::vector<SerializableObject::Retainer<T>> Composition::each_child(
    ErrorStatus* error_status,
    optional<TimeRange> search_range,
    bool shallow_search) const
{
    std::vector<Retainer<Composable>> children;
    if (search_range)
    {
        auto range_map = range_of_all_children(error_status);
        if (!error_status)
            return {};

        // find the first item whose end_time_inclusive is after the
        // start_time of the search range
        const auto first_inside_range = _bisect_left(
            search_range->start_time(),
            [&range_map](Composable* child) { return range_map[child].end_time_inclusive(); },
            error_status);
        if (!error_status)
            return {};

        // find the last item whose start_time is before the
        // end_time_inclusive of the search_range
        const auto last_in_range = _bisect_right(
            search_range->end_time_inclusive(),
            [&range_map](Composable* child) { return range_map[child].start_time(); },
            error_status,
            first_inside_range);
        if (!error_status)
            return {};

        // limit the search to children who are in the search_range
        for (auto child = _children.begin() + first_inside_range; child < _children.begin() + last_in_range; ++child)
            children.push_back(child->value);
    }
    else
    {
        // otherwise search all the children
        children = _children;
    }
    std::vector<Retainer<T>> out;
    for (const auto& child : children)
    {
        if (auto valid_child = dynamic_cast<T*>(child.value))
            out.push_back(valid_child);

        // if not a shallow_search, for children that are compositions,
        // recurse into their children
        if (!shallow_search)
            if (auto composition = dynamic_cast<Composition*>(child.value))
            {
                if (search_range)
                {
                    search_range = transformed_time_range(*search_range, composition, error_status);
                    if (!error_status)
                        return {};
                }

                const auto valid_children = composition->each_child<T>(error_status, search_range, shallow_search);
                if (!error_status)
                    return {};
                for (const auto& valid_child : valid_children)
                    out.push_back(valid_child);
            }
    }
    return out;
}

// Return the index of the last item in seq such that all e in seq[:index]
// have key_func(e) <= tgt, and all e in seq[index:] have key_func(e) > tgt.
// 
// Thus, seq.insert(index, value) will insert value after the rightmost item
// such that meets the above condition.
// 
// lower_search_boundand upper_search_bound bound the slice to be searched.
// 
// Assumes that seq is already sorted.
inline size_t Composition::_bisect_right(
    RationalTime const& tgt,
    std::function<RationalTime(Composable*)> const& key_func,
    ErrorStatus* error_status,
    optional<size_t> lower_search_bound,
    optional<size_t> upper_search_bound) const
{
    if (*lower_search_bound < 0)
    {
        error_status->outcome = ErrorStatus::Outcome::INTERNAL_ERROR;
        error_status->details = "lower_search_bound must be non-negative";
        return 0;
    }
    if (!upper_search_bound)
        *upper_search_bound = _children.size();
    size_t midpoint_index = 0;
    while (*lower_search_bound < *upper_search_bound)
    {
        midpoint_index = static_cast<size_t>(std::floor((*lower_search_bound + *upper_search_bound) / 2.0));

        if (tgt < key_func(_children[midpoint_index]))
            upper_search_bound = midpoint_index;
        else
            lower_search_bound = midpoint_index + 1;
    }

    return *lower_search_bound;
}

// Return the index of the last item in seq such that all e in seq[:index]
// have key_func(e) < tgt, and all e in seq[index:] have key_func(e) >= tgt.
//
// Thus, seq.insert(index, value) will insert value before the leftmost item
// such that meets the above condition.
//
// lower_search_boundand upper_search_bound bound the slice to be searched.
//
// Assumes that seq is already sorted.
inline size_t Composition::_bisect_left(
    RationalTime const& tgt,
    std::function<RationalTime(Composable*)> const& key_func,
    ErrorStatus* error_status,
    optional<size_t> lower_search_bound,
    optional<size_t> upper_search_bound) const
{
    if (*lower_search_bound < 0)
    {
        error_status->outcome = ErrorStatus::Outcome::INTERNAL_ERROR;
        error_status->details = "lower_search_bound must be non-negative";
        return 0;
    }
    if (!upper_search_bound)
        *upper_search_bound = _children.size();
    size_t midpoint_index = 0;
    while (*lower_search_bound < *upper_search_bound)
    {
        midpoint_index = static_cast<size_t>(std::floor((*lower_search_bound + *upper_search_bound) / 2.0));

        if (key_func(_children[midpoint_index]) < tgt)
            lower_search_bound = midpoint_index + 1;
        else
            upper_search_bound = midpoint_index;
    }

    return *lower_search_bound;
}

} }

