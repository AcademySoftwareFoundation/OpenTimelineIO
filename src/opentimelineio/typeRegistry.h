// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentimelineio/errorStatus.h"
#include "opentimelineio/version.h"

#include <algorithm>
#include <functional>
#include <map>
#include <mutex>
#include <string>
#include <unordered_map>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION_NS {

class SerializableObject;
class Encoder;
class AnyDictionary;

/// @name Schema Typedefs
///
/// typedefs for the schema downgrading system.
///
/// @todo Should we make version an int64_t? That would match what we can
/// serialize natively, since we only serialize 64 bit signed ints.
///@{

using schema_version_map = std::unordered_map<std::string, int64_t>;
using label_to_schema_version_map =
    std::unordered_map<std::string, schema_version_map>;

///@}

extern const label_to_schema_version_map CORE_VERSION_MAP;

/// @brief Type registry.
class OTIO_API_TYPE TypeRegistry
{
public:
    /// @brief Get the type registry singleton.
    ///
    /// Access to functions are thread-safe.
    static TypeRegistry& instance();

    /// @brief Register a new schema.
    ///
    /// This API call should only be needed by developers who are creating a bridge
    /// to another language (e.g. Python, Swift).  In a C++ environment, prefer
    /// the templated form of this call.
    ///
    /// If the specified schema_name has already been registered, this function does nothing and returns false.
    bool register_type(
        std::string const&                   schema_name,
        int                                  schema_version,
        std::type_info const*                type,
        std::function<SerializableObject*()> create,
        std::string const&                   class_name = "");

    /// @brief Register a new SerializableObject class
    ///
    /// If the specified schema_name has already been registered, this function does nothing and returns false.
    /// If you need to provide an alias for a schema name, se register_type_from_existing_type().
    template <typename CLASS>
    bool register_type()
    {
        return register_type(
            CLASS::Schema::name,
            CLASS::Schema::version,
            &typeid(CLASS),
            []() -> SerializableObject* { return new CLASS; },
            CLASS::Schema::name);
    }

    /// @brief Register a new schema.
    ///
    /// This API call can be used to register an alternate schema name for a class, in
    /// case a schema name is changed and the old name needs to be allowed as well.
    ///
    /// On success, returns true; otherwise, returns false and sets error_status if non-null.
    bool register_type_from_existing_type(
        std::string const& schema_name,
        int                schema_version,
        std::string const& existing_schema_name,
        ErrorStatus*       error_status = nullptr);

    /// This API call should only be needed by developers who are creating a bridge
    /// to another language (e.g. Python, Swift).  In a C++ environment, prefer
    /// the templated form of this call.

    /// @brief Register a function that will upgrade the given schema to version_to_upgrade_to.
    ///
    /// Note that as a schema is upgraded, older upgrade functions should be kept around;
    /// the intent is that each upgrade function upgrades the schema from the version
    /// just before version_to_upgrade_to.  (I.e. all registered upgrade functions are
    /// run in order, on the same data dictionary.)
    ///
    /// Returns false if an upgrade function has been registered for this (schema_name, version)
    /// pair, or if schema_name itself has not been registered, and true otherwise.
    bool register_upgrade_function(
        std::string const&                  schema_name,
        int                                 version_to_upgrade_to,
        std::function<void(AnyDictionary*)> upgrade_function);

    /// @brief Convenience API for C++ developers.
    ///
    /// See the documentation of the non-templated register_upgrade_function() for details.
    template <typename CLASS>
    bool register_upgrade_function(
        int                                 version_to_upgrade_to,
        std::function<void(AnyDictionary*)> upgrade_function)
    {
        return register_upgrade_function(
            CLASS::schema_name,
            version_to_upgrade_to,
            upgrade_function);
    }

    /// @brief Downgrade function from version_to_downgrade_from to
    /// version_to_downgrade_from - 1
    bool register_downgrade_function(
        std::string const&                  schema_name,
        int                                 version_to_downgrade_from,
        std::function<void(AnyDictionary*)> downgrade_function);

    /// @brief Convenience API for C++ developers.
    ///
    /// See the documentation of the non-templated register_downgrade_function() for details.
    template <typename CLASS>
    bool register_downgrade_function(
        int                                 version_to_upgrade_to,
        std::function<void(AnyDictionary*)> upgrade_function)
    {
        return register_downgrade_function(
            CLASS::schema_name,
            version_to_upgrade_to,
            upgrade_function);
    }

    /// @brief Return the instance from the given schema.
    SerializableObject* instance_from_schema(
        std::string const& schema_name,
        int                schema_version,
        AnyDictionary&     dict,
        ErrorStatus*       error_status = nullptr)
    {
        return _instance_from_schema(
            schema_name,
            schema_version,
            dict,
            false /* internal_read */,
            error_status);
    }

    /// @brief For use by external bridging systems.
    bool set_type_record(
        SerializableObject*,
        std::string const& schema_name,
        ErrorStatus*       error_status = nullptr);

    /// @brief For inspecting the type registry, build a map of schema name to version.
    void type_version_map(schema_version_map& result);

private:
    TypeRegistry();

    TypeRegistry(TypeRegistry const&)            = delete;
    TypeRegistry& operator=(TypeRegistry const&) = delete;

    class _TypeRecord
    {
        std::string                          schema_name;
        int                                  schema_version;
        std::string                          class_name;
        std::function<SerializableObject*()> create;

        std::map<int, std::function<void(AnyDictionary*)>> upgrade_functions;
        std::map<int, std::function<void(AnyDictionary*)>> downgrade_functions;

        _TypeRecord(
            std::string                          _schema_name,
            int                                  _schema_version,
            std::string                          _class_name,
            std::function<SerializableObject*()> _create)
        {
            this->schema_name    = _schema_name;
            this->schema_version = _schema_version;
            this->class_name     = _class_name;
            this->create         = _create;
        }

        SerializableObject* create_object() const;

        friend class TypeRegistry;
        friend class SerializableObject;
        friend class CloningEncoder;
    };

    // helper functions for lookup
    _TypeRecord* _find_type_record(std::string const& key)
    {
        auto it = _type_records.find(key);
        return it == _type_records.end() ? nullptr : it->second;
    }

    SerializableObject* _instance_from_schema(
        std::string    schema_name,
        int            schema_version,
        AnyDictionary& dict,
        bool           internal_read,
        ErrorStatus*   error_status = nullptr);

    static std::pair<std::string, int>
                 _schema_and_version_from_label(std::string const& label);
    _TypeRecord* _lookup_type_record(std::string const& schema_name);
    _TypeRecord* _lookup_type_record(std::type_info const& type);

    std::mutex                          _registry_mutex;
    std::map<std::string, _TypeRecord*> _type_records;
    std::map<std::string, _TypeRecord*> _type_records_by_type_name;

    friend class SerializableObject;
    friend class CloningEncoder;
};

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION_NS
