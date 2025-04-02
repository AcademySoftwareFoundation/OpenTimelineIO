// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/version.h"

#include <Imath/ImathBox.h>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Composition;

/// @brief An object that can be composed within a Composition (such as a Track or Stack).
class Composable : public SerializableObjectWithMetadata
{
public:
    /// @brief This struct provides the Composable schema.
    struct Schema
    {
        static auto constexpr name   = "Composable";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    /// @brief Create a new composable.
    ///
    /// @param name The name of the composable.
    /// @param metadata The metadata for the clip.
    Composable(
        std::string const&   name     = std::string(),
        AnyDictionary const& metadata = AnyDictionary());

    /// @brief Return whether the composable is visible.
    virtual bool visible() const;

    /// @brief Return whether the composable is overlapping another item.
    virtual bool overlapping() const;

    /// @brief Return the parent composition.
    Composition* parent() const { return _parent; }

    /// @brief Return the duration of the composable.
    virtual RationalTime duration(ErrorStatus* error_status = nullptr) const;

    /// @brief Return the available image bounds.
    virtual std::optional<IMATH_NAMESPACE::Box2d>
    available_image_bounds(ErrorStatus* error_status) const;

protected:
    bool        _set_parent(Composition*) noexcept;
    Composable* _highest_ancestor() noexcept;

    Composable const* _highest_ancestor() const noexcept
    {
        return const_cast<Composable*>(this)->_highest_ancestor();
    }

    virtual ~Composable();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    Composition* _parent;
    friend class Composition;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
