// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentimelineio/composition.h"
#include "opentimelineio/clip.h"
#include "opentimelineio/vectorIndexing.h"

#include <assert.h>
#include <set>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

Composition::Composition(
    std::string const&              name,
    std::optional<TimeRange> const& source_range,
    AnyDictionary const&            metadata,
    std::vector<Effect*> const&     effects,
    std::vector<Marker*> const&     markers)
    : Parent(name, source_range, metadata, effects, markers)
{}

Composition::~Composition()
{
    clear_children();
}

std::string
Composition::composition_kind() const
{
    static std::string kind = "Composition";
    return kind;
}

void
Composition::clear_children()
{
    for (Composable* child: _children)
    {
        child->_set_parent(nullptr);
    }

    _children.clear();
    _child_set.clear();
}

bool
Composition::set_children(
    std::vector<Composable*> const& children,
    ErrorStatus*                    error_status)
{
    for (auto child: children)
    {
        if (child->parent())
        {
            if (error_status)
            {
                *error_status = ErrorStatus::CHILD_ALREADY_PARENTED;
            }
            return false;
        }
    }

    for (auto child: children)
    {
        child->_set_parent(this);
    }

    _children  = decltype(_children)(children.begin(), children.end());
    _child_set = std::set<Composable*>(children.begin(), children.end());
    return true;
}

bool
Composition::insert_child(
    int          index,
    Composable*  child,
    ErrorStatus* error_status)
{
    if (child->parent())
    {
        if (error_status)
        {
            *error_status = ErrorStatus::CHILD_ALREADY_PARENTED;
        }
        return false;
    }

    child->_set_parent(this);

    index = adjusted_vector_index(index, _children);
    if (index >= int(_children.size()))
    {
        _children.emplace_back(child);
    }
    else
    {
        _children.insert(_children.begin() + std::max(index, 0), child);
    }

    _child_set.insert(child);
    return true;
}

bool
Composition::set_child(int index, Composable* child, ErrorStatus* error_status)
{
    index = adjusted_vector_index(index, _children);
    if (index < 0 || index >= int(_children.size()))
    {
        if (error_status)
        {
            *error_status = ErrorStatus::ILLEGAL_INDEX;
        }
        return false;
    }

    if (_children[index] != child)
    {
        if (child->parent())
        {
            if (error_status)
            {
                *error_status = ErrorStatus::CHILD_ALREADY_PARENTED;
            }
            return false;
        }

        _children[index]->_set_parent(nullptr);
        _child_set.erase(_children[index]);
        child->_set_parent(this);
        _children[index] = child;
        _child_set.insert(child);
    }
    return true;
}

bool
Composition::remove_child(int index, ErrorStatus* error_status)
{
    if (_children.empty())
    {
        if (error_status)
        {
            *error_status = ErrorStatus::ILLEGAL_INDEX;
        }
        return false;
    }

    index = adjusted_vector_index(index, _children);

    _child_set.erase(_children[index]);

    if (size_t(index) >= _children.size())
    {
        _children.back()->_set_parent(nullptr);
        _children.pop_back();
    }
    else
    {
        index = std::max(index, 0);
        _children[index]->_set_parent(nullptr);
        _children.erase(_children.begin() + index);
    }

    return true;
}

int
Composition::index_of_child(Composable const* child, ErrorStatus* error_status)
    const
{
    for (size_t i = 0; i < _children.size(); i++)
    {
        if (_children[i] == child)
        {
            return int(i);
        }
    }

    if (error_status)
    {
        *error_status                = ErrorStatus::NOT_A_CHILD_OF;
        error_status->object_details = this;
    }
    return -1;
}

bool
Composition::read_from(Reader& reader)
{
    if (reader.read("children", &_children) && Parent::read_from(reader))
    {
        for (Composable* child: _children)
        {
            if (!child->_set_parent(this))
            {
                reader.error(ErrorStatus::CHILD_ALREADY_PARENTED);
                return false;
            }
        }
    }
    return true;
}

void
Composition::write_to(Writer& writer) const
{
    Parent::write_to(writer);
    writer.write("children", _children);
}

bool
Composition::is_parent_of(Composable const* other) const
{
    Composition const* cur_parent = other->_parent;
    if (cur_parent == this)
        return true;

    std::set<Composition const*> visited;
    while (cur_parent && visited.count(cur_parent) == 0)
    {
        if (cur_parent == this)
            return true;

        visited.insert(cur_parent);
        cur_parent = cur_parent->_parent;
    }
    return false;
}

std::pair<std::optional<RationalTime>, std::optional<RationalTime>>
Composition::handles_of_child(
    Composable const* /* child */,
    ErrorStatus* /* error_status */) const
{
    return std::make_pair(
        std::optional<RationalTime>(),
        std::optional<RationalTime>());
}

std::vector<Composition*>
Composition::_path_from_child(
    Composable const* child,
    ErrorStatus*      error_status) const
{
    auto                      current = child->parent();
    std::vector<Composition*> parents{ current };

    while (current != this)
    {
        current = current->parent();
        if (!current)
        {
            if (error_status)
            {
                *error_status                = ErrorStatus::NOT_DESCENDED_FROM;
                error_status->object_details = this;
            }
            return parents;
        }
        parents.push_back(current);
    }

    return parents;
}

TimeRange
Composition::range_of_child_at_index(int /* index */, ErrorStatus* error_status)
    const
{
    if (error_status)
    {
        *error_status = ErrorStatus::NOT_IMPLEMENTED;
    }
    return TimeRange();
}

TimeRange
Composition::trimmed_range_of_child_at_index(
    int /* index */,
    ErrorStatus* error_status) const
{
    if (error_status)
    {
        *error_status = ErrorStatus::NOT_IMPLEMENTED;
    }
    return TimeRange();
}

std::map<Composable*, TimeRange>
Composition::range_of_all_children(ErrorStatus* error_status) const
{
    if (error_status)
    {
        *error_status = ErrorStatus::NOT_IMPLEMENTED;
    }
    return std::map<Composable*, TimeRange>();
}

// XXX should have reference_space argument or something
TimeRange
Composition::range_of_child(Composable const* child, ErrorStatus* error_status)
    const
{
    auto parents = _path_from_child(child, error_status);
    if (is_error(error_status))
    {
        return TimeRange();
    }

    Composition const*       reference_space = this; // XXX
    std::optional<TimeRange> result_range;
    auto                     current = child;

    assert(!parents.empty());
    for (auto parent: parents)
    {
        const int index = parent->index_of_child(current, error_status);
        if (is_error(error_status))
        {
            return TimeRange();
        }

        auto parent_range =
            parent->range_of_child_at_index(index, error_status);
        if (is_error(error_status))
        {
            return TimeRange();
        }

        if (!result_range)
        {
            result_range = parent_range;
            current      = parent;
            continue;
        }

        result_range = TimeRange(
            result_range->start_time() + parent_range.start_time(),
            std::min(result_range->duration(), parent_range.duration()));
        current = parent;
    }

    return (reference_space != this) ? transformed_time_range(
                                           *result_range,
                                           reference_space,
                                           error_status)
                                     : *result_range;
}

// XXX should have reference_space argument or something
std::optional<TimeRange>
Composition::trimmed_range_of_child(
    Composable const* child,
    ErrorStatus*      error_status) const
{
    auto parents = _path_from_child(child, error_status);
    if (is_error(error_status))
    {
        return TimeRange();
    }

    std::optional<TimeRange> result_range;
    auto                     current = child;

    assert(!parents.empty());
    for (auto parent: parents)
    {
        const int index = parent->index_of_child(current, error_status);
        if (is_error(error_status))
        {
            return TimeRange();
        }

        auto parent_range =
            parent->trimmed_range_of_child_at_index(index, error_status);
        if (is_error(error_status))
        {
            return TimeRange();
        }

        if (!result_range)
        {
            result_range = parent_range;
            current      = parent;
            continue;
        }

        result_range = TimeRange(
            result_range->start_time() + parent_range.start_time(),
            std::min(result_range->duration(), parent_range.duration()));
    }

    if (!source_range())
    {
        return result_range;
    }

    auto new_start_time =
        std::max(source_range()->start_time(), result_range->start_time());
    if (new_start_time > result_range->end_time_exclusive())
    {
        return std::nullopt;
    }

    auto new_duration = std::min(
                            result_range->end_time_exclusive(),
                            source_range()->end_time_exclusive())
                        - new_start_time;
    if (new_duration.value() < 0)
    {
        return std::nullopt;
    }

    return TimeRange(new_start_time, new_duration);
}

std::vector<Composable*>
Composition::_children_at_time(RationalTime t, ErrorStatus* error_status) const
{
    std::vector<Composable*> result;

    // range_of_child_at_index is O(i), so this loop is quadratic:
    for (size_t i = 0; i < _children.size() && !is_error(error_status); i++)
    {
        if (range_of_child_at_index(int(i), error_status).contains(t))
        {
            result.push_back(_children[i]);
        }
    }

    return result;
}

std::optional<TimeRange>
Composition::trim_child_range(TimeRange child_range) const
{
    if (!source_range())
    {
        return child_range;
    }

    const TimeRange sr = *source_range();
    bool past_end_time = sr.start_time() >= child_range.end_time_exclusive();
    bool before_start_time =
        sr.end_time_exclusive() <= child_range.start_time();

    if (past_end_time || before_start_time)
    {
        return std::nullopt;
    }

    if (child_range.start_time() < sr.start_time())
    {
        child_range = TimeRange::range_from_start_end_time(
            sr.start_time(),
            child_range.end_time_exclusive());
    }

    if (child_range.end_time_exclusive() > sr.end_time_exclusive())
    {
        child_range = TimeRange::range_from_start_end_time(
            child_range.start_time(),
            sr.end_time_exclusive());
    }

    return child_range;
}

bool
Composition::has_child(Composable* child) const
{
    return _child_set.find(child) != _child_set.end();
}

SerializableObject::Retainer<Composable>
Composition::child_at_time(
    RationalTime const& search_time,
    ErrorStatus*        error_status,
    bool                shallow_search) const
{
    Retainer<Composable> result;

    auto range_map = range_of_all_children(error_status);
    if (is_error(error_status))
    {
        return result;
    }

    // find the first item whose end_time_exclusive is after the
    const auto first_inside_range = _bisect_left(
        search_time,
        [&range_map](Composable* child) {
            return range_map[child].end_time_exclusive();
        },
        error_status);
    if (is_error(error_status))
    {
        return result;
    }

    // find the last item whose start_time is before the
    const auto last_in_range = _bisect_right(
        search_time,
        [&range_map](Composable* child) {
            return range_map[child].start_time();
        },
        error_status,
        first_inside_range);
    if (is_error(error_status))
    {
        return result;
    }

    // limit the search to children who are in the search_range
    std::vector<Retainer<Composable>> possible_matches;
    for (auto child = _children.begin() + first_inside_range;
         child < _children.begin() + last_in_range;
         ++child)
    {
        possible_matches.push_back(child->value);
    }
    for (const auto& thing: possible_matches)
    {
        if (range_map[thing].overlaps(search_time))
        {
            result = thing;
            break;
        }
    }

    // if the search cannot or should not continue
    auto composition =
        Retainer<Composition>(dynamic_cast<Composition*>(result.value));
    if (!result || shallow_search || !composition)
    {
        return result;
    }

    // before you recurse, you have to transform the time into the
    // space of the child
    const auto child_search_time =
        transformed_time(search_time, composition.value, error_status);
    if (is_error(error_status))
    {
        return result;
    }

    result = composition.value->child_at_time(
        child_search_time,
        error_status,
        shallow_search);
    if (is_error(error_status))
    {
        return result;
    }
    return result;
}

std::vector<SerializableObject::Retainer<Composable>>
Composition::children_in_range(
    TimeRange const& search_range,
    ErrorStatus*     error_status) const
{
    std::vector<Retainer<Composable>> children;

    auto range_map = range_of_all_children(error_status);
    if (is_error(error_status))
    {
        return children;
    }

    // find the first item whose end_time_inclusive is after the
    // start_time of the search range
    const auto first_inside_range = _bisect_left(
        search_range.start_time(),
        [&range_map](Composable* child) {
            return range_map[child].end_time_inclusive();
        },
        error_status);
    if (is_error(error_status))
    {
        return children;
    }

    // find the last item whose start_time is before the
    // end_time_inclusive of the search_range
    const auto last_in_range = _bisect_right(
        search_range.end_time_inclusive(),
        [&range_map](Composable* child) {
            return range_map[child].start_time();
        },
        error_status,
        first_inside_range);
    if (is_error(error_status))
    {
        return children;
    }

    // limit the search to children who are in the search_range
    for (auto child = _children.begin() + first_inside_range;
         child < _children.begin() + last_in_range;
         ++child)
    {
        children.push_back(child->value);
    }
    return children;
}

int64_t
Composition::_bisect_right(
    RationalTime const&                             tgt,
    std::function<RationalTime(Composable*)> const& key_func,
    ErrorStatus*                                    error_status,
    std::optional<int64_t>                          lower_search_bound,
    std::optional<int64_t>                          upper_search_bound) const
{
    if (*lower_search_bound < 0)
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::Outcome::INTERNAL_ERROR,
                "lower_search_bound must be non-negative");
        }
        return 0;
    }
    if (!upper_search_bound)
    {
        upper_search_bound = std::optional<int64_t>(_children.size());
    }
    int64_t midpoint_index = 0;
    while (*lower_search_bound < *upper_search_bound)
    {
        midpoint_index = static_cast<int64_t>(
            std::floor((*lower_search_bound + *upper_search_bound) / 2.0));

        if (tgt < key_func(_children[midpoint_index]))
        {
            upper_search_bound = midpoint_index;
        }
        else
        {
            lower_search_bound = midpoint_index + 1;
        }
    }

    return *lower_search_bound;
}

int64_t
Composition::_bisect_left(
    RationalTime const&                             tgt,
    std::function<RationalTime(Composable*)> const& key_func,
    ErrorStatus*                                    error_status,
    std::optional<int64_t>                          lower_search_bound,
    std::optional<int64_t>                          upper_search_bound) const
{
    if (*lower_search_bound < 0)
    {
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::Outcome::INTERNAL_ERROR,
                "lower_search_bound must be non-negative");
        }
        return 0;
    }
    if (!upper_search_bound)
    {
        upper_search_bound = std::optional<int64_t>(_children.size());
    }
    int64_t midpoint_index = 0;
    while (*lower_search_bound < *upper_search_bound)
    {
        midpoint_index = static_cast<int64_t>(
            std::floor((*lower_search_bound + *upper_search_bound) / 2.0));

        if (key_func(_children[midpoint_index]) < tgt)
        {
            lower_search_bound = midpoint_index + 1;
        }
        else
        {
            upper_search_bound = midpoint_index;
        }
    }

    return *lower_search_bound;
}

bool
Composition::has_clips() const
{
    for (auto child: children())
    {
        if (dynamic_cast<Clip*>(child.value))
        {
            return true;
        }
        else if (auto child_comp = dynamic_cast<Composition*>(child.value))
        {
            if (child_comp->has_clips())
            {
                return true;
            }
        }
    }
    return false;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
