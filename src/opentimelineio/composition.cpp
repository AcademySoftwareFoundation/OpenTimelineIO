#include "opentimelineio/composition.h"
#include "opentimelineio/vectorIndexing.h"

#include <assert.h>
#include <set>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
Composition::Composition(std::string const& name,
                         optional<TimeRange> const& source_range,
                         AnyDictionary const& metadata,
         std::vector<Effect*> const& effects,
         std::vector<Marker*> const& markers)
    : Parent(name, source_range, metadata, effects, markers)
{
}

Composition::~Composition() {
    clear_children();
}

std::string const& Composition::composition_kind() const {
    static std::string kind = "Composition";
    return kind;
}

void 
Composition::clear_children() {
    for (Composable* child: _children) {
        child->_set_parent(nullptr);
    }

    _children.clear();
    _child_set.clear();
}

bool 
Composition::set_children(std::vector<Composable*> const& children, ErrorStatus* error_status) {
    for (auto child : children) {
        if (child->parent()) {
            *error_status = ErrorStatus::CHILD_ALREADY_PARENTED;
            return false;
        }
    }

    for (auto child : children) {
        child->_set_parent(this);
    }

    _children = decltype(_children)(children.begin(), children.end());
    _child_set = std::set<Composable*>(children.begin(), children.end());
    return true;
}

bool 
Composition::insert_child(int index, Composable* child, ErrorStatus* error_status) {
    if (child->parent()) {
        *error_status = ErrorStatus::CHILD_ALREADY_PARENTED;
        return false;
    }

    child->_set_parent(this);
        
    index = adjusted_vector_index(index, _children);
    if (index >= int(_children.size())) {
        _children.emplace_back(child);
    }
    else {
        _children.insert(_children.begin() + std::max(index, 0), child);
    }

    _child_set.insert(child);
    return true;
}

bool 
Composition::set_child(int index, Composable* child, ErrorStatus* error_status) {
    index = adjusted_vector_index(index, _children);
    if (index < 0 || index >= int(_children.size())) {
        *error_status = ErrorStatus::ILLEGAL_INDEX;
        return false;
    }

    if (_children[index] != child) {
        if (child->parent()) {
            *error_status = ErrorStatus::CHILD_ALREADY_PARENTED;
            return false;
        }
        
        _children[index].value->_set_parent(nullptr);
        _child_set.erase(_children[index]);
        child->_set_parent(this);
        _children[index] = child;
        _child_set.insert(child);
    }
    return true;
}

bool 
Composition::remove_child(int index, ErrorStatus* error_status) {
    if (_children.empty()) {
        *error_status = ErrorStatus::ILLEGAL_INDEX;
        return false;
    }

    index = adjusted_vector_index(index, _children);

    _child_set.erase(_children[index]);
    
    if (size_t(index) >= _children.size()) {
        _children.back().value->_set_parent(nullptr);
        _children.pop_back();
    }
    else {
        index = std::max(index, 0);
        _children[index].value->_set_parent(nullptr);
        _children.erase(_children.begin() + index);
    }

    return true;
}

bool Composition::read_from(Reader& reader) {
    if (reader.read("children", &_children) &&
        Parent::read_from(reader)) {
        for (Composable* child : _children) {
            if (!child->_set_parent(this)) {
                reader.error(ErrorStatus::CHILD_ALREADY_PARENTED);
                return false;
            }
        }
    }
    return true;
}

void Composition::write_to(Writer& writer) const {
    Parent::write_to(writer);
    writer.write("children", _children);
}

bool Composition::is_parent_of(Composable const* other) const {
    Composition const* cur_parent = other->_parent;
    if (cur_parent == this)
        return true;
    
    std::set<Composition const*> visited;
    while (cur_parent && visited.count(cur_parent) == 0) {
        if (cur_parent == this)
            return true;

        visited.insert(cur_parent);
        cur_parent = cur_parent->_parent;
    }
    return false;
}

std::pair<optional<RationalTime>, optional<RationalTime>>
Composition::handles_of_child(Composable const* /* child */, ErrorStatus* /* error_status */) const {
    return std::make_pair(optional<RationalTime>(), optional<RationalTime>());
}

int Composition::_index_of_child(Composable const* child, ErrorStatus* error_status) const {
    for (size_t i = 0; i < _children.size(); i++) {
        if (_children[i].value == child) {
            return int(i);
        }
    }
    
    *error_status = ErrorStatus::NOT_A_CHILD_OF;
    error_status->object_details = this;
    return -1;
}

std::vector<Composition*> Composition::_path_from_child(Composable const* child,
                                                        ErrorStatus* error_status) const {
    auto current = child->parent();
    std::vector<Composition*> parents { current };
    
    while (current != this) {
        current = current->parent();
        if (!current) {
            *error_status = ErrorStatus::NOT_DESCENDED_FROM;
            error_status->object_details = this;
            return parents;
        }
        parents.push_back(current);
    }

    return parents;
}

TimeRange Composition::range_of_child_at_index(int /* index */, ErrorStatus* error_status) const {
    *error_status = ErrorStatus::NOT_IMPLEMENTED;
    return TimeRange();
}

TimeRange Composition::trimmed_range_of_child_at_index(int /* index */, ErrorStatus* error_status) const {
    *error_status = ErrorStatus::NOT_IMPLEMENTED;
    return TimeRange();
}

std::map<Composable*, TimeRange>
Composition::range_of_all_children(ErrorStatus* error_status) const {
    *error_status = ErrorStatus::NOT_IMPLEMENTED;
    return std::map<Composable*, TimeRange>();
}

// XXX should have reference_space argument or something
TimeRange Composition::range_of_child(Composable const* child, ErrorStatus* error_status) const {
    auto parents = _path_from_child(child, error_status);
    if (*error_status) {
        return TimeRange();
    }
    
    Composition const* reference_space = this;    // XXX
    optional<TimeRange> result_range;
    auto current = child;
    
    assert(!parents.empty());
    for (auto parent: parents) {
        auto index = parent->_index_of_child(current, error_status);
        if (*error_status) {
            return TimeRange();
        }

        auto parent_range = parent->range_of_child_at_index(index, error_status);
        if (*error_status) {
            return TimeRange();
        }
        
        if (!result_range) {
            result_range = parent_range;
            current = parent;
            continue;
        }

         result_range = TimeRange(result_range->start_time() + parent_range.start_time(),
                                   result_range->duration());
        current = parent;
    }
    
    return (reference_space != this) ? transformed_time_range(*result_range, reference_space, error_status) : *result_range;
}

// XXX should have reference_space argument or something
optional<TimeRange> Composition::trimmed_range_of_child(Composable const* child, ErrorStatus* error_status) const {
    auto parents = _path_from_child(child, error_status);
    if (*error_status) {
        return TimeRange();
    }
    
    optional<TimeRange> result_range;
    auto current = child;
    
    assert(!parents.empty());
    for (auto parent: parents) {
        auto index = parent->_index_of_child(current, error_status);
        if (*error_status) {
            return TimeRange();
        }

        auto parent_range = parent->trimmed_range_of_child_at_index(index, error_status);
        if (*error_status) {
            return TimeRange();
        }
        
        if (!result_range) {
            result_range = parent_range;
            current = parent;
            continue;
        }
        
        result_range = TimeRange(result_range->start_time() + parent_range.start_time(),
                                  result_range->duration());
    }
    
    if (!source_range()) {
        return result_range;
    }
    
    auto new_start_time = std::max(source_range()->start_time(), result_range->start_time());
    if (new_start_time > result_range->end_time_exclusive()) {
        return nullopt;
    }
    
    auto new_duration = std::min(result_range->end_time_exclusive(),
                                 source_range()->end_time_exclusive()) - new_start_time;
    if (new_duration.value() < 0) {
        return nullopt;
    }
    
    return TimeRange(new_start_time, new_duration);
}

std::vector<Composable*> Composition::_children_at_time(RationalTime t, ErrorStatus* error_status) const {
    std::vector<Composable*> result;
    
    // range_of_child_at_index is O(i), so this loop is quadratic:
    for (size_t i = 0; i < _children.size() && !(*error_status); i++) {
        if (range_of_child_at_index(int(i), error_status).contains(t)) {
            result.push_back(_children[i].value);
        }
    }
    
    return result;
}

optional<TimeRange> Composition::trim_child_range(TimeRange child_range) const {
    if (!source_range()) {
        return child_range;
    }
    
    TimeRange const& sr = *source_range();
    bool past_end_time = sr.start_time() >= child_range.end_time_exclusive();
    bool before_start_time = sr.end_time_exclusive() <= child_range.start_time();
    
    if (past_end_time|| before_start_time) {
        return nullopt;
    }
            
    if (child_range.start_time() < sr.start_time()) {
        child_range = TimeRange::range_from_start_end_time(sr.start_time(),
                                                           child_range.end_time_exclusive());
    }
    
    if (child_range.end_time_exclusive() > sr.end_time_exclusive()) {
        child_range = TimeRange::range_from_start_end_time(child_range.start_time(),
                                                           sr.end_time_exclusive());
    }

    return child_range;
}

bool Composition::has_child(Composable* child) const {
    return _child_set.find(child) != _child_set.end();
}

} }
