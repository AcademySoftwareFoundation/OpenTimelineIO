#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/composition.h"
#include "opentimelineio/serializableObjectWithMetadata.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {

class Clip;

class SerializableCollection : public SerializableObjectWithMetadata {
public:
    struct Schema {
        static auto constexpr name = "SerializableCollection";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    SerializableCollection(std::string const& name = std::string(),
                           std::vector<SerializableObject*> children = std::vector<SerializableObject*>(),
                           AnyDictionary const& metadata = AnyDictionary());

    std::vector<Retainer<SerializableObject>> const& children() const {
        return _children;
    }

    std::vector<Retainer<SerializableObject>>& children() {
        return _children;
    }

    void set_children(std::vector<SerializableObject*> const& children);

    void clear_children();
    
    void insert_child(int index, SerializableObject* child);

    bool set_child(int index, SerializableObject* child, ErrorStatus* error_status);

    bool remove_child(int index, ErrorStatus* error_status);

    // Return a vector of clips.
    //
    // An optional search_range may be provided to limit the search.
    //
    // If shallow_search is false, will recurse into children.
    std::vector<Retainer<Clip> > clip_if(
        ErrorStatus* error_status,
        optional<TimeRange> const& search_range = nullopt,
        bool shallow_search = false) const;

    // Return a vector of all objects that match the given template type.
    //
    // An optional search_range may be provided to limit the search.
    //
    // If shallow_search is false, will recurse into children.
    template<typename T = Composable>
    std::vector<Retainer<T>> children_if(
        ErrorStatus* error_status,
        optional<TimeRange> search_range = nullopt,
        bool shallow_search = false) const;

    // Return the first object that matches the given template type.
    //
    // An optional search_range may be provided to limit the search.
    //
    // If shallow_search is false, will recurse into children.
    template<typename T = Composable>
    Retainer<T> child_if(
        ErrorStatus* error_status,
        optional<TimeRange> search_range = nullopt,
        bool shallow_search = false) const;

protected:
    virtual ~SerializableCollection();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    enum ChildrenIfOptions {
        match_first = 1,
        shallow_search = 2
    };
    template<typename T = Composable>
    std::vector<Retainer<T>> _children_if(
        ErrorStatus* error_status,
        optional<TimeRange> search_range,
        int options) const;

    std::vector<Retainer<SerializableObject>> _children;
};

template<typename T>
inline std::vector<SerializableObject::Retainer<T>> SerializableCollection::children_if(
    ErrorStatus* error_status,
    optional<TimeRange> search_range,
    bool shallow_search) const
{
    int options = 0;
    if (shallow_search)
    {
        options |= ChildrenIfOptions::shallow_search;
    }
    return _children_if<T>(error_status, search_range, options);
}

template<typename T>
inline SerializableObject::Retainer<T> SerializableCollection::child_if(
    ErrorStatus* error_status,
    optional<TimeRange> search_range,
    bool shallow_search) const
{
    int options = ChildrenIfOptions::match_first;
    if (shallow_search)
    {
        options |= ChildrenIfOptions::shallow_search;
    }
    const auto l = _children_if<T>(error_status, search_range, options);
    return !l.empty() ? l[0] : nullptr;
}

template<typename T>
inline std::vector<SerializableObject::Retainer<T>> SerializableCollection::_children_if(
    ErrorStatus* error_status,
    optional<TimeRange> search_range,
    int options) const
{
    std::vector<Retainer<T>> out;
    for (const auto& child : _children)
    {
        // filter out children who are not descended from the specified type
        if (auto valid_child = dynamic_cast<T*>(child.value))
        {
            out.push_back(valid_child);
            if (options & ChildrenIfOptions::match_first)
            {
                break;
            }
        }

        // if not a shallow_search, for children that are serialiable collections or compositions,
        // recurse into their children
        if (!(options & ChildrenIfOptions::shallow_search))
        {
            if (auto collection = dynamic_cast<SerializableCollection*>(child.value))
            {
                const auto valid_children = collection->_children_if<T>(error_status, search_range, options);
                if (!error_status) {
                    *error_status = ErrorStatus(ErrorStatus::INTERNAL_ERROR, "one or more invalid children encountered");
                }
                for (const auto& valid_child : valid_children) {
                    out.push_back(valid_child);
                }
                if (!out.empty() && (options & ChildrenIfOptions::match_first))
                {
                    break;
                }
            }
            else if (auto composition = dynamic_cast<Composition*>(child.value))
            {
                std::vector<Retainer<T>> valid_children;
                if (options & ChildrenIfOptions::match_first)
                {
                    if (auto valid_child = composition->child_if<T>(error_status, search_range, options & ChildrenIfOptions::shallow_search))
                    {
                        valid_children.push_back(valid_child);
                    }
                }
                else
                {
                    valid_children = composition->children_if<T>(error_status, search_range, options & ChildrenIfOptions::shallow_search);
                }
                if (!error_status) {
                    *error_status = ErrorStatus(ErrorStatus::INTERNAL_ERROR, "one or more invalid children encountered");
                }
                for (const auto& valid_child : valid_children) {
                    out.push_back(valid_child);
                }
                if (!out.empty() && (options & ChildrenIfOptions::match_first))
                {
                    break;
                }
            }
        }
    }
    return out;
}

} }
