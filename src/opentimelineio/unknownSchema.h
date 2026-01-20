// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/serializableObject.h"
#include "opentimelineio/version.h"

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

/// @brief An unknown schema.
class OTIO_API_TYPE UnknownSchema : public SerializableObject
{
public:
    /// @brief This struct provides the UnknownSchema schema.
    struct Schema
    {
        static auto constexpr name   = "UnknownSchema";
        static int constexpr version = 1;
    };

    /// @brief Create a new unknown schema.
    ///
    /// @param original_schema_name The original schema name.
    /// @param original_schema_version The original schema version.
    UnknownSchema(
        std::string const& original_schema_name,
        int                original_schema_version);

    /// @brief Return the original schema name.
    std::string original_schema_name() const noexcept
    {
        return _original_schema_name;
    }

    /// @brief Return the original schema version.
    int original_schema_version() const noexcept
    {
        return _original_schema_version;
    }

    AnyDictionary data() const noexcept
    {
        return _data;
    }

    bool read_from(Reader&) override;
    void write_to(Writer&) const override;

    bool is_unknown_schema() const override;

protected:
    virtual ~UnknownSchema();

    std::string _schema_name_for_reference() const override;

private:
    std::string _original_schema_name;
    int         _original_schema_version;

    AnyDictionary _data;

    friend class TypeRegistry;
    friend class SerializableObject::Writer;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
