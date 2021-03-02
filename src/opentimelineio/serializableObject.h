#pragma once

#include "opentimelineio/version.h"
#include "opentimelineio/errorStatus.h"
#include "opentimelineio/anyVector.h"
#include "opentimelineio/anyDictionary.h"
#include "opentimelineio/optional.h"
#include "opentimelineio/typeRegistry.h"
#include "opentimelineio/stringUtils.h"
#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentime/timeTransform.h"

#include <list>
#include <type_traits>

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION  {
    
class SerializableObject {
public:
    struct Schema {
        static auto constexpr name = "SerializableObject";
        static int constexpr version = 1;
    };

    SerializableObject();

    /*
     * You cannot directly delete a SerializableObject* (or, hopefully, anything
     * derived from it, as all derivations are required to protect the destructor).
     *
     * Instead, call the member funtion possibly_delete(), which deletes the object
     * (and, recursively, the objects owned by this object), provided the objects
     * are not under external management (e.g. prevented from being deleted because an
     * external scripting system is holding a reference to them).
     */
    bool possibly_delete();

    bool to_json_file(std::string const& file_name, ErrorStatus* error_status, int indent = 4) const;
    std::string to_json_string(ErrorStatus* error_status, int indent = 4) const;

    static SerializableObject* from_json_file(std::string const& file_name, ErrorStatus* error_status);
    static SerializableObject* from_json_string(std::string const& input, ErrorStatus* error_status);

    bool is_equivalent_to(SerializableObject const& other) const;

    // Makes a (deep) clone of this instance.
    //
    // Descendent SerializableObjects are cloned as well.
    // If the operation fails, nullptr is returned and error_status
    // is set appropriately.
    SerializableObject* clone(ErrorStatus* error_status) const;

    // Allow external system (e.g. Python, Swifft) to add serializable fields
    // on the fly.  C++ implementations should have no need for this functionality.
    AnyDictionary& dynamic_fields() {
        return _dynamic_fields;
    }

    template <typename T = SerializableObject> struct Retainer;

    class Reader {
    public:
        void debug_dict() {
            for (auto e: _dict) {
                printf("Key: %s\n", e.first.c_str());
            }
        }
        
        bool read(std::string const& key, bool* dest);
        bool read(std::string const& key, int* dest);
        bool read(std::string const& key, double* dest);
        bool read(std::string const& key, std::string* dest);
        bool read(std::string const& key, RationalTime* dest);
        bool read(std::string const& key, TimeRange* dest);
        bool read(std::string const& key, class TimeTransform* dest);
        bool read(std::string const& key, AnyVector* dest);
        bool read(std::string const& key, AnyDictionary* dest);
        bool read(std::string const& key, any* dest);

        bool read(std::string const& key, optional<bool>* dest);
        bool read(std::string const& key, optional<int>* dest);
        bool read(std::string const& key, optional<double>* dest);
        bool read(std::string const& key, optional<RationalTime>* dest);
        bool read(std::string const& key, optional<TimeRange>* dest);
        bool read(std::string const& key, optional<TimeTransform>* dest);
        // skipping std::string because we translate null into the empty
        // string, so the conversion is somewhat ambiguous

        // no other optionals are allowed:
        template <typename T>
        bool read(std::string const& key, optional<T>* dest) = delete;

        template <typename T>
        bool read(std::string const& key, T* dest) {
            any a;
            return read(key, &a) && _from_any(a, dest);
        }

        template <typename T>
        bool read(std::string const& key, Retainer<T>* dest) {
            SerializableObject* so;
            if (!read(key, &so)) {
                return false;
            }

            if (!so) {
                *dest = Retainer<T>();
                return true;
            }

            if (T* tso = dynamic_cast<T*>(so)) {
                *dest = Retainer<T>(tso);
                return true;
            }
            
            _error(ErrorStatus(ErrorStatus::TYPE_MISMATCH,
                               string_printf("Expected object of type %s; read type %s instead",
                                             demangled_type_name(typeid(T)).c_str(),
                                             demangled_type_name(so).c_str())));
            return false;
        }

        bool has_key(std::string const& key) {
            return _dict.find(key) != _dict.end();
        }
        
        template <typename T>
        bool read_if_present(std::string const& key, T* dest) {
            return has_key(key) ? read(key, dest) : true;
        }

        void error(ErrorStatus const& error_status) {
            _error(error_status);
        }

    private:
        typedef std::function<void (ErrorStatus const&)> error_function_t;

        struct _Resolver {
            std::map<SerializableObject*, AnyDictionary> data_for_object;
            std::map<std::string, SerializableObject*> object_for_id;
            std::map<SerializableObject*, int> line_number_for_object;

            void finalize(error_function_t error_function) {
                for (auto e: data_for_object) {
                    int line_number = line_number_for_object[e.first];
                    Reader::_fix_reference_ids(e.second, error_function, *this, line_number);
                    Reader r(e.second, error_function, e.first, line_number);
                    e.first->read_from(r);
                }
            }
        };
            
        any _decode(_Resolver& resolver);

        template <typename T>
        bool _from_any(any const& source, std::vector<T>* dest) {
            if (!_type_check(typeid(AnyVector), source.type())) {
                return false;
            }
            
            AnyVector const& av = any_cast<AnyVector const&>(source);
            std::vector<T> result;
            result.reserve(av.size());

            for (auto e: av) {
                T elem;
                if (!_from_any(e, &elem)) {
                    break;
                }
                
                result.emplace_back(elem);
            }

            dest->swap(result);
            return true;
        }

        template <typename T>
        bool _from_any(any const& source, std::list<T>* dest) {
            if (!_type_check(typeid(AnyVector), source.type())) {
                return false;
            }
            
            AnyVector const& av = any_cast<AnyVector const&>(source);
            std::list<T> result;

            for (auto e: av) {
                T elem;
                if (!_from_any(e, &elem)) {
                    break;
                }
                
                result.emplace_back(elem);
            }

            dest->swap(result);
            return true;
        }

        template <typename T>
        bool _from_any(any const& source, std::map<std::string, T>* dest) {
            if (!_type_check(typeid(AnyDictionary), source.type())) {
                return false;
            }
            
            AnyDictionary const& dict = any_cast<AnyDictionary const&>(source);
            std::map<std::string, T> result;

            for (auto e: dict) {
                T elem;
                if (!_from_any(e.second, &elem)) {
                    break;
                }
                
                result.emplace(e.first, elem);
            }

            dest->swap(result);
            return true;
        }

        template <typename T>
        bool _from_any(any const& source, T** dest) {
            if (source.type() == typeid(void)) {
                *dest = nullptr;
                return true;
            }

            if (!_type_check_so(typeid(Retainer<>), source.type(), typeid(T))) {
                return false;
            }
            
            SerializableObject* so = any_cast<SerializableObject::Retainer<>>(source).value;
            if (!so) {
                *dest = nullptr;
            }
            else if (T* tptr = dynamic_cast<T*>(so)) {
                *dest = tptr;
            }
            else {
                _type_check_so(typeid(T), typeid(*so), typeid(T));
                return false;
            }
            return true;
        }

        template <typename T>
        bool _from_any(any const& source, Retainer<T>* dest) {
            if (!_type_check_so(typeid(Retainer<>), source.type(), typeid(T))) {
                return false;
            }

            Retainer<> const& rso = any_cast<Retainer<> const &>(source);
            if (!rso.value) {
                *dest = Retainer<T>(nullptr);
                return true;
            }
            else if (T* tptr = dynamic_cast<T*>(rso.value)) {
                *dest = Retainer<T>(tptr);
                return true;
            }

            _type_check_so(typeid(T), typeid(*rso.value), typeid(T));
            return false;
        }

        template <typename T>
        bool _from_any(any const& source, T* dest) {
            if (!_type_check(typeid(T), source.type())) {
                return false;
            }
            
            *dest = any_cast<T>(source);
            return true;
        }

        Reader(AnyDictionary&, error_function_t const& error_function,
               SerializableObject* source, int line_number = -1);

        void _error(ErrorStatus const& error_status);

        template <typename T>
        bool _fetch(std::string const& key, T* dest, bool* had_null = nullptr);

        template <typename T>
        bool _read_optional(std::string const& key, optional<T>* value);

        bool _fetch(std::string const& key, int64_t* dest);
        bool _fetch(std::string const& key, double* dest);
        bool _fetch(std::string const& key, SerializableObject** dest);
        bool _type_check(std::type_info const& wanted, std::type_info const& found);
        bool _type_check_so(std::type_info const& wanted, std::type_info const& found,
                            std::type_info const& so_type);

        static void _fix_reference_ids(AnyDictionary&, error_function_t const& error_function,
                                       _Resolver&, int line_number);
        static void _fix_reference_ids(any&, error_function_t const& error_function,
                                       _Resolver&, int line_number);

        Reader(Reader const&) = delete;
        Reader operator=(Reader const&) = delete;

        AnyDictionary _dict;
        error_function_t const& _error_function;
        SerializableObject* _source;
        int _line_number;

        friend class UnknownSchema;
        friend class JSONDecoder;
        friend class CloningEncoder;
        friend class SerializableObject;
        friend class TypeRegistry;
    };
    
    class Writer {
    public:
        static bool write_root(any const& value, class Encoder& encoder, ErrorStatus* error_status);

        void write(std::string const& key, bool value);
        void write(std::string const& key, int64_t value);
        void write(std::string const& key, double value);
        void write(std::string const& key, std::string const& value);
        void write(std::string const& key, RationalTime value);
        void write(std::string const& key, TimeRange value);
        void write(std::string const& key, optional<RationalTime> value);
        void write(std::string const& key, optional<TimeRange> value);
        void write(std::string const& key, class TimeTransform value);
        void write(std::string const& key, SerializableObject const* value);
        void write(std::string const& key, SerializableObject* value) {
            write(key, (SerializableObject const*)(value));
        }
        void write(std::string const& key, AnyDictionary const& value);
        void write(std::string const& key, AnyVector const& value);
        void write(std::string const& key, any const& value);

        template <typename T>
        void write(std::string const& key, T const& value) {
            write(key, _to_any(value));
        }
        
        template <typename T>
        void write(std::string const& key, Retainer<T> const& retainer) {
            write(key, retainer.value);
        }

    private:
        /*
         * Convience routines for converting various STL structures of specific
         * types to a parallel hierarchy holding anys.
         */
        template <typename T>
        static any _to_any(std::vector<T> const& value) {
            AnyVector av;
            av.reserve(value.size());

            for (auto e: value) {
                av.emplace_back(_to_any(e));
            }

            return any(std::move(av));
        }
            
        template <typename T>
        static any _to_any(std::map<std::string, T> const& value) {
            AnyDictionary am;
            for (auto e: value) {
                am.emplace(e.first, _to_any(e.second));
            }

            return any(std::move(am));
        }

        template <typename T>
        static any _to_any(std::list<T> const& value) {
            AnyVector av;
            av.reserve(value.size());

            for (auto e: value) {
                av.emplace_back(_to_any(e));
            }

            return any(std::move(av));
        }

        template <typename T>
        static any _to_any(T const* value) {
            SerializableObject* so = (SerializableObject*) value;
            return any(SerializableObject::Retainer<>(so));
        }

        template <typename T>
        static any _to_any(T* value) {
            SerializableObject* so = (SerializableObject*) value;
            return any(SerializableObject::Retainer<>(so));
        }

        template <typename T>
        static any _to_any(Retainer<T> const& value) {
            SerializableObject* so = value.value;
            return any(SerializableObject::Retainer<>(so));
        }

        template <typename T>
        static any _to_any(T const& value) {
            return any(value);
        }
        
        Writer(class Encoder& encoder)
            : _encoder(encoder) {
            _build_dispatch_tables();
        }

        Writer(Writer const&) = delete;
        Writer operator=(Writer const&) = delete;

        void _build_dispatch_tables();
        void _write(std::string const& key, any const& value);
        void _encoder_write_key(std::string const& key);

        bool _any_dict_equals(any const& lhs, any const& rhs);
        bool _any_array_equals(any const& lhs, any const& rhs);
        bool _any_equals(any const& lhs, any const& rhs);

        std::string _no_key;
        std::map<std::type_info const*, std::function<void (any const&)>> _write_dispatch_table;
        std::map<std::type_info const*, std::function<bool (any const&, any const&)>> _equality_dispatch_table;

        std::map<std::string, std::function<void (any const&)>> _write_dispatch_table_by_name;
        std::map<SerializableObject const*, std::string> _id_for_object;
        std::map<std::string, int> _next_id_for_type;

        class Encoder& _encoder;
        friend class SerializableObject;
    };

    virtual bool read_from(Reader&);
    virtual void write_to(Writer&) const;

    virtual bool is_unknown_schema() const;
    
    std::string const& schema_name() const {
        return _type_record()->schema_name;
    }

    int schema_version() const {
        return _type_record()->schema_version;
    }
    
    template <typename T>
    struct Retainer {
        operator T* () const {
            return value;
        }
        
        operator bool () const {
            return value != nullptr;
        }
        
        Retainer(T const* so = nullptr)
            : value((T*) so) {
            if (value)
                value->_managed_retain();
        }
        
        Retainer(Retainer const& rhs)
            : value(rhs.value) {
            if (value)
                value->_managed_retain();
        }

        Retainer& operator=(Retainer const& rhs) {
            if (rhs.value)
                rhs.value->_managed_retain();
            if (value)
                value->_managed_release();
            value = rhs.value;
            return *this;
        }
                
        ~Retainer() {
            if (value)
                value->_managed_release();
        }

        T* take_value() {
            if (!value)
                return nullptr;
            
            T* ptr = value;
            value = nullptr;
            ptr->_managed_ref_count--;
            return ptr;
        }

        T* value;
    };
    
protected:
    virtual ~SerializableObject();
    virtual bool _is_deletable();

private:
    SerializableObject(SerializableObject const&) = delete;
    SerializableObject& operator=(SerializableObject const&) = delete;
    template <typename T> friend struct Retainer;
    
    virtual std::string const& _schema_name_for_reference() const;
            
    void _managed_retain();
    void _managed_release();

public:
    struct ReferenceId {
        std::string id;
        friend bool operator==(ReferenceId lhs, ReferenceId rhs) {
            return lhs.id == rhs.id;
        }
    };

    void install_external_keepalive_monitor(std::function<void ()> monitor, bool apply_now);

    int current_ref_count() const;
    
    struct UnknownType {
        std::string type_name;
    };
    
private:
    void _set_type_record(TypeRegistry::_TypeRecord const* type_record) {
        _cached_type_record = type_record;
    }
    
    TypeRegistry::_TypeRecord const* _type_record() const;

    mutable TypeRegistry::_TypeRecord const* _cached_type_record;
    int _managed_ref_count;
    std::function<void ()> _external_keepalive_monitor;

    mutable std::mutex _mutex;

    AnyDictionary _dynamic_fields;
    friend class TypeRegistry;
};
    
} }
