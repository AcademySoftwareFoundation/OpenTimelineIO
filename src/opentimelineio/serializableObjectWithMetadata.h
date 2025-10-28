// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObject.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief A serializable object with metadata.
class OTIO_API_TYPE SerializableObjectWithMetadata : public SerializableObject
{
public:
    /// @brief This struct provides the SerializableObjectWithMetadata schema.
    struct Schema
    {
        static auto constexpr name   = "SerializableObjectWithMetadata";
        static int constexpr version = 1;
    };

    using Parent = SerializableObject;

    /// @brief Create a new serializable object.
    ///
    /// @param name The object name.
    /// @param metadata The metadata for the object.
    OTIO_API SerializableObjectWithMetadata(
        std::string const&   name     = std::string(),
        AnyDictionary const& metadata = AnyDictionary());

    /// @brief Return the object name.
    std::string name() const noexcept { return _name; }

    /// @brief Set the object name.
    void set_name(std::string const& name) { _name = name; }

    /// @brief Modify the object metadata.
    AnyDictionary& metadata() noexcept { return _metadata; }

    /// @brief Return the object metadata.
    AnyDictionary metadata() const noexcept { return _metadata; }

protected:
    virtual ~SerializableObjectWithMetadata();

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

private:
    std::string   _name;
    AnyDictionary _metadata;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
