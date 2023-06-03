// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObjectWithMetadata.h"
#include "opentimelineio/version.h"

#include <ImathBox.h>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class Composition;

class Composable : public SerializableObjectWithMetadata
{
public:
    struct Schema
    {
        static auto constexpr name   = "Composable";
        static int constexpr version = 1;
    };

    using Parent = SerializableObjectWithMetadata;

    Composable(
        std::string const&   name     = std::string(),
        AnyDictionary const& metadata = AnyDictionary());

    virtual bool visible() const;
    virtual bool overlapping() const;

    Composition* parent() const { return _parent; }

    virtual RationalTime duration(ErrorStatus* error_status = nullptr) const;

    virtual optional<IMATH_NAMESPACE::Box2d>
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
