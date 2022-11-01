// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/composition.h"
#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/timeline.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Clip;

class SerializableCollection : public SerializableObjectWithMetadata
{
public:
    struct Schema
    {
        static auto constexpr name   = "SerializableCollection";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    SerializableCollection(
        std::string const&               name = std::string(),
        std::vector<SerializableObject*> children =
            std::vector<SerializableObject*>(),
        AnyDictionary const& metadata = AnyDictionary());

    std::vector<Retainer<SerializableObject>> const& children() const noexcept
    {
        return _children;
    }

    std::vector<Retainer<SerializableObject>>& children() noexcept
    {
        return _children;
    }

    void set_children(std::vector<SerializableObject*> const& children);

    void clear_children();

    void insert_child(int index, SerializableObject* child);

    bool set_child(
        int                 index,
        SerializableObject* child,
        ErrorStatus*        error_status = nullptr);

    bool remove_child(int index, ErrorStatus* error_status = nullptr);

    // Return child clips.
    //
    // An optional search_range may be provided to limit the search.
    //
    // If shallow_search is false, will recurse into children.
    std::vector<Retainer<Clip>> clip_if(
        ErrorStatus*               error_status   = nullptr,
        optional<TimeRange> const& search_range   = nullopt,
        bool                       shallow_search = false) const;

    // Return all child clips recursively.
    std::vector<Retainer<Clip>> all_clips(
        ErrorStatus* error_status = nullptr) const;

    // Return child objects that match the given template type.
    //
    // An optional search_time may be provided to limit the search.
    //
    // If shallow_search is false, will recurse into children.
    template <typename T = Composable>
    std::vector<Retainer<T>> children_if(
        ErrorStatus*        error_status   = nullptr,
        optional<TimeRange> search_range   = nullopt,
        bool                shallow_search = false) const;

    // Return all child objects recursively.
    std::vector<Retainer<Composable>> all_children(
        ErrorStatus* error_status = nullptr) const;

protected:
    virtual ~SerializableCollection();

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

private:
    std::vector<Retainer<SerializableObject>> _children;
};

template <typename T>
inline std::vector<SerializableObject::Retainer<T>>
SerializableCollection::children_if(
    ErrorStatus*        error_status,
    optional<TimeRange> search_range,
    bool                shallow_search) const
{
    std::vector<Retainer<T>> out;
    for (const auto& child: _children)
    {
        // filter out children who are not descended from the specified type
        if (auto valid_child = dynamic_cast<T*>(child.value))
        {
            out.push_back(valid_child);
        }

        // if not a shallow_search, for children that are serializable collections,
        // compositions, or timelines, recurse into their children
        if (!shallow_search)
        {
            if (auto collection =
                    dynamic_cast<SerializableCollection*>(child.value))
            {
                const auto valid_children =
                    collection->children_if<T>(error_status, search_range);
                if (is_error(error_status))
                {
                    return out;
                }
                for (const auto& valid_child: valid_children)
                {
                    out.push_back(valid_child);
                }
            }
            else if (auto composition = dynamic_cast<Composition*>(child.value))
            {
                const auto valid_children =
                    composition->children_if<T>(error_status, search_range);
                if (is_error(error_status))
                {
                    return out;
                }
                for (const auto& valid_child: valid_children)
                {
                    out.push_back(valid_child);
                }
            }
            else if (auto timeline = dynamic_cast<Timeline*>(child.value))
            {
                const auto valid_children =
                    timeline->children_if<T>(error_status, search_range);
                if (is_error(error_status))
                {
                    return out;
                }
                for (const auto& valid_child: valid_children)
                {
                    out.push_back(valid_child);
                }
            }
        }
    }
    return out;
}

inline std::vector<SerializableObject::Retainer<Composable>>
SerializableCollection::all_children(ErrorStatus* error_status) const
{
    return children_if<Composable>(error_status);
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
