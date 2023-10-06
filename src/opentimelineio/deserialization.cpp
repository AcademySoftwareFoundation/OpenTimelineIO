// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "opentime/rationalTime.h"
#include "opentime/timeRange.h"
#include "opentime/timeTransform.h"
#include "opentimelineio/serializableObject.h"
#include "opentimelineio/serializableObjectWithMetadata.h"
#include "stringUtils.h"

#define RAPIDJSON_NAMESPACE OTIO_rapidjson
#include <rapidjson/cursorstreamwrapper.h>
#include <rapidjson/error/en.h>
#include <rapidjson/filereadstream.h>
#include <rapidjson/reader.h>

#if defined(_WINDOWS)
#    ifndef WIN32_LEAN_AND_MEAN
#        define WIN32_LEAN_AND_MEAN
#    endif // WIN32_LEAN_AND_MEAN
#    ifndef NOMINMAX
#        define NOMINMAX
#    endif // NOMINMAX
#    include <windows.h>
#endif

namespace opentimelineio { namespace OPENTIMELINEIO_VERSION {

class JSONDecoder : public OTIO_rapidjson::
                        BaseReaderHandler<OTIO_rapidjson::UTF8<>, JSONDecoder>
{
public:
    JSONDecoder(std::function<size_t()> line_number_function)
        : _line_number_function{ line_number_function }
    {
        using namespace std::placeholders;
        _error_function = std::bind(&JSONDecoder::_error, this, _1);
    }

    bool has_errored(ErrorStatus* error_status)
    {
        if (error_status)
        {
            *error_status = _error_status;
        }
        return is_error(_error_status);
    }

    bool has_errored() { return is_error(_error_status); }

    void finalize()
    {
        if (!has_errored())
        {
            _resolver.finalize(_error_function);
        }
    }

    bool Null() { return store(any()); }
    bool Bool(bool b) { return store(any(b)); }

    // coerce all integer types to int64_t...
    bool Int(int i) { return store(any(static_cast<int64_t>(i))); }
    bool Int64(int64_t i) { return store(any(static_cast<int64_t>(i))); }
    bool Uint(unsigned u) { return store(any(static_cast<int64_t>(u))); }
    bool Uint64(uint64_t u)
    {
        /// prevent an overflow
        return store(any(static_cast<int64_t>(u & 0x7FFFFFFFFFFFFFFF)));
    }

    // ...and all floating point types to double
    bool Double(double d) { return store(any(d)); }

    bool
    String(const char* str, OTIO_rapidjson::SizeType length, bool /* copy */)
    {
        return store(any(std::string(str, length)));
    }

    bool Key(const char* str, OTIO_rapidjson::SizeType length, bool /* copy */)
    {
        if (has_errored())
        {
            return false;
        }

        if (_stack.empty() || !_stack.back().is_dict)
        {
            _internal_error(
                "RapidJSONDecoder:: _handle_key called while not decoding an object");
            return false;
        }

        _stack.back().cur_key = std::string(str, length);
        return true;
    }

    bool StartArray()
    {
        if (has_errored())
        {
            return false;
        }

        _stack.emplace_back(_DictOrArray{ false /* is_dict*/ });
        return true;
    }

    bool StartObject()
    {
        if (has_errored())
        {
            return false;
        }

        _stack.emplace_back(_DictOrArray{ true /* is_dict*/ });
        return true;
    }

    bool EndArray(OTIO_rapidjson::SizeType)
    {
        if (has_errored())
        {
            return false;
        }

        if (_stack.empty())
        {
            _internal_error(
                "RapidJSONDecoder::_handle_end_array() called without matching _handle_start_array()");
        }
        else
        {
            auto& top = _stack.back();
            if (top.is_dict)
            {
                _internal_error(
                    "RapidJSONDecoder::_handle_end_array() called without matching _handle_start_array()");
                _stack.pop_back();
            }
            else
            {
                AnyVector va;
                va.swap(top.array);
                _stack.pop_back();
                store(any(std::move(va)));
            }
        }
        return true;
    }

    bool EndObject(OTIO_rapidjson::SizeType)
    {
        if (has_errored())
        {
            return false;
        }

        if (_stack.empty())
        {
            _internal_error(
                "JSONDecoder::_handle_end_object() called without matching _handle_start_object()");
        }
        else
        {
            auto& top = _stack.back();
            if (!top.is_dict)
            {
                _internal_error(
                    "JSONDecoder::_handle_end_object() called without matching _handle_start_object");
                _stack.pop_back();
            }
            else
            {
                // when we end a dictionary, we immediately convert it
                // to the type it really represents, if it is a schema object.
                SerializableObject::Reader reader(
                    top.dict,
                    _error_function,
                    nullptr,
                    static_cast<int>(_line_number_function()));
                _stack.pop_back();
                store(reader._decode(_resolver));
            }
        }
        return true;
    }

    bool store(any&& a)
    {
        if (has_errored())
        {
            return false;
        }

        if (_stack.empty())
        {
            _root.swap(a);
        }
        else
        {
            auto& top = _stack.back();
            if (top.is_dict)
            {
                top.dict.emplace(_stack.back().cur_key, a);
            }
            else
            {
                top.array.emplace_back(a);
            }
        }
        return true;
    }

    template <typename T>
    static T const* _lookup(AnyDictionary const& d, std::string const& key)
    {
        auto e = d.find(key);
        if (e != d.end() && typeid(T) == e->second.type())
        {
            return &any_cast<const T&>(e->second);
        }
        return nullptr;
    }

    any _root;

    void _internal_error(std::string const& err_msg)
    {
        _error_status = ErrorStatus(
            ErrorStatus::INTERNAL_ERROR,
            string_printf(
                "%s (near line %d)",
                err_msg.c_str(),
                _line_number_function()));
    }

    void _error(ErrorStatus const& error_status)
    {
        _error_status = error_status;
    }

    ErrorStatus _error_status;

    struct _DictOrArray
    {
        _DictOrArray(bool is_dict) { this->is_dict = is_dict; }

        bool          is_dict;
        AnyDictionary dict;
        AnyVector     array;
        std::string   cur_key;
    };

    std::vector<_DictOrArray>               _stack;
    std::function<void(ErrorStatus const&)> _error_function;
    std::function<size_t()>                 _line_number_function;

    SerializableObject::Reader::_Resolver _resolver;
};

SerializableObject::Reader::Reader(
    AnyDictionary&          source,
    error_function_t const& error_function,
    SerializableObject*     so,
    int                     line_number)
    : _error_function(error_function)
    , _source(so)
    , _line_number(line_number)
{
    // destructively read from source.  Decoding it will either return it back
    // anyway, or convert it to another type, in which case we want to destroy
    // the original so as to not keep extra data around.
    _dict.swap(source);
}

void
SerializableObject::Reader::_error(ErrorStatus const& error_status)
{
    if (!_source)
    {
        if (_line_number > 0)
        {
            _error_function(ErrorStatus(
                error_status.outcome,
                string_printf("near line %d", _line_number)));
        }
        else
        {
            _error_function(error_status);
        }
        return;
    }

    std::string line_description;
    if (_line_number > 0)
    {
        line_description = string_printf(" (near line %d)", _line_number);
    }

    std::string name = "<unknown>";
    auto        e    = _dict.find("name");
    if (e != _dict.end() && e->second.type() == typeid(std::string))
    {
        name = any_cast<std::string>(e->second);
    }

    _error_function(ErrorStatus(
        error_status.outcome,
        string_printf(
            "While reading object named '%s' (of type '%s'): %s%s",
            name.c_str(),
            type_name_for_error_message(_source).c_str(),
            error_status.details.c_str(),
            line_description.c_str())));
}

void
SerializableObject::Reader::_fix_reference_ids(
    AnyDictionary&          m,
    error_function_t const& error_function,
    _Resolver&              resolver,
    int                     line_number)
{
    for (auto& e: m)
    {
        _fix_reference_ids(e.second, error_function, resolver, line_number);
    }
}

void
SerializableObject::Reader::_fix_reference_ids(
    any&                    a,
    error_function_t const& error_function,
    _Resolver&              resolver,
    int                     line_number)
{
    if (a.type() == typeid(AnyDictionary))
    {
        _fix_reference_ids(
            any_cast<AnyDictionary&>(a),
            error_function,
            resolver,
            line_number);
    }
    else if (a.type() == typeid(AnyVector))
    {
        AnyVector& child_array = any_cast<AnyVector&>(a);
        for (size_t i = 0; i < child_array.size(); i++)
        {
            _fix_reference_ids(
                child_array[i],
                error_function,
                resolver,
                line_number);
        }
    }
    else if (a.type() == typeid(SerializableObject::ReferenceId))
    {
        std::string id = any_cast<SerializableObject::ReferenceId>(a).id;
        auto        e  = resolver.object_for_id.find(id);
        if (e == resolver.object_for_id.end())
        {
            error_function(ErrorStatus(
                ErrorStatus::UNRESOLVED_OBJECT_REFERENCE,
                string_printf("%s (near line %d)", id.c_str(), line_number)));
        }
        else
        {
            a = any(Retainer<>(e->second));
        }
    }
}

template <typename T>
bool
SerializableObject::Reader::_fetch(
    std::string const& key,
    T*                 dest,
    bool*              had_null)
{
    auto e = _dict.find(key);
    if (e == _dict.end())
    {
        _error(ErrorStatus(ErrorStatus::KEY_NOT_FOUND, key));
        return false;
    }
    else if (e->second.type() == typeid(void) && had_null)
    {
        _dict.erase(e);
        *had_null = true;
        return true;
    }
    else if (e->second.type() != typeid(T))
    {
        _error(ErrorStatus(
            ErrorStatus::TYPE_MISMATCH,
            string_printf(
                "expected type %s under key '%s': found type %s instead",
                type_name_for_error_message(typeid(T)).c_str(),
                key.c_str(),
                type_name_for_error_message(e->second.type()).c_str())));
        return false;
    }

    if (had_null)
    {
        *had_null = false;
    }

    std::swap(*dest, any_cast<T&>(e->second));
    _dict.erase(e);
    return true;
}

bool
SerializableObject::Reader::_fetch(std::string const& key, double* dest)
{
    auto e = _dict.find(key);
    if (e == _dict.end())
    {
        _error(ErrorStatus(ErrorStatus::KEY_NOT_FOUND, key));
        return false;
    }

    if (e->second.type() == typeid(double))
    {
        *dest = any_cast<double>(e->second);
        _dict.erase(e);
        return true;
    }
    else if (e->second.type() == typeid(int))
    {
        *dest = static_cast<double>(any_cast<int>(e->second));
        _dict.erase(e);
        return true;
    }
    else if (e->second.type() == typeid(int64_t))
    {
        *dest = static_cast<double>(any_cast<int64_t>(e->second));
        _dict.erase(e);
        return true;
    }

    _error(ErrorStatus(
        ErrorStatus::TYPE_MISMATCH,
        string_printf(
            "expected type %s under key '%s': found type %s instead",
            type_name_for_error_message(typeid(double)).c_str(),
            key.c_str(),
            type_name_for_error_message(e->second.type()).c_str())));
    return false;
}

bool
SerializableObject::Reader::_fetch(std::string const& key, int64_t* dest)
{
    auto e = _dict.find(key);
    if (e == _dict.end())
    {
        _error(ErrorStatus(ErrorStatus::KEY_NOT_FOUND, key));
        return false;
    }

    if (e->second.type() == typeid(int64_t))
    {
        *dest = any_cast<int64_t>(e->second);
        _dict.erase(e);
        return true;
    }
    else if (e->second.type() == typeid(int))
    {
        *dest = any_cast<int>(e->second);
        _dict.erase(e);
        return true;
    }

    _error(ErrorStatus(
        ErrorStatus::TYPE_MISMATCH,
        string_printf(
            "expected type %s under key '%s': found type %s instead",
            type_name_for_error_message(typeid(int64_t)).c_str(),
            key.c_str(),
            type_name_for_error_message(e->second.type()).c_str())));
    return false;
}

bool
SerializableObject::Reader::_fetch(
    std::string const&   key,
    SerializableObject** dest)
{
    auto e = _dict.find(key);
    if (e == _dict.end())
    {
        _error(ErrorStatus(ErrorStatus::KEY_NOT_FOUND, key));
        return false;
    }

    if (e->second.type() == typeid(void))
    {
        *dest = nullptr;
        _dict.erase(e);
        return true;
    }
    else if (e->second.type() != typeid(SerializableObject::Retainer<>))
    {
        _error(ErrorStatus(
            ErrorStatus::TYPE_MISMATCH,
            string_printf(
                "expected SerializableObject* under key '%s': found type %s instead",
                key.c_str(),
                type_name_for_error_message(e->second.type()).c_str())));
        return false;
    }

    *dest = any_cast<SerializableObject::Retainer<>>(e->second);
    _dict.erase(e);
    return true;
}

bool
SerializableObject::Reader::_type_check(
    std::type_info const& wanted,
    std::type_info const& found)
{
    if (wanted != found)
    {
        _error(ErrorStatus(
            ErrorStatus::TYPE_MISMATCH,
            string_printf(
                "while decoding complex STL type, expected type '%s', found type '%s' instead",
                type_name_for_error_message(wanted).c_str(),
                type_name_for_error_message(found).c_str())));
        return false;
    }
    return true;
}

bool
SerializableObject::Reader::_type_check_so(
    std::type_info const& wanted,
    std::type_info const& found,
    std::type_info const& so_type)
{
    if (wanted != found)
    {
        _error(ErrorStatus(
            ErrorStatus::TYPE_MISMATCH,
            string_printf(
                "expected to read a %s, found a %s instead",
                type_name_for_error_message(so_type).c_str(),
                type_name_for_error_message(found).c_str())));
        return false;
    }
    return true;
}

any
SerializableObject::Reader::_decode(_Resolver& resolver)
{
    if (_dict.find("OTIO_SCHEMA") == _dict.end())
    {
        return any(std::move(_dict));
    }

    std::string schema_name_and_version;

    if (!_fetch("OTIO_SCHEMA", &schema_name_and_version))
    {
        return any();
    }

    if (schema_name_and_version == "RationalTime.1")
    {
        double rate, value;
        return _fetch("rate", &rate) && _fetch("value", &value)
                   ? any(RationalTime(value, rate))
                   : any();
    }
    else if (schema_name_and_version == "TimeRange.1")
    {
        RationalTime start_time, duration;
        return _fetch("start_time", &start_time)
                       && _fetch("duration", &duration)
                   ? any(TimeRange(start_time, duration))
                   : any();
    }
    else if (schema_name_and_version == "TimeTransform.1")
    {
        RationalTime offset;
        double       rate, scale;
        return _fetch("offset", &offset) && _fetch("rate", &rate)
                       && _fetch("scale", &scale)
                   ? any(TimeTransform(offset, scale, rate))
                   : any();
    }
    else if (schema_name_and_version == "SerializableObjectRef.1")
    {
        std::string ref_id;
        if (!_fetch("id", &ref_id))
        {
            return any();
        }

        return any(SerializableObject::ReferenceId{ ref_id });
    }
    else if (schema_name_and_version == "V2d.1")
    {
        double x, y;
        return _fetch("x", &x) && _fetch("y", &y)
                   ? any(IMATH_NAMESPACE::V2d(x, y))
                   : any();
    }
    else if (schema_name_and_version == "Box2d.1")
    {
        IMATH_NAMESPACE::V2d min, max;
        return _fetch("min", &min) && _fetch("max", &max)
                   ? any(IMATH_NAMESPACE::Box2d(std::move(min), std::move(max)))
                   : any();
    }
    else
    {
        std::string ref_id;
        if (_dict.find("OTIO_REF_ID") != _dict.end())
        {
            if (!_fetch("OTIO_REF_ID", &ref_id))
            {
                return any();
            }

            auto e = resolver.object_for_id.find(ref_id);
            if (e != resolver.object_for_id.end())
            {
                _error(ErrorStatus(
                    ErrorStatus::DUPLICATE_OBJECT_REFERENCE,
                    ref_id));
                return any();
            }
        }

        TypeRegistry& r = TypeRegistry::instance();
        std::string   schema_name;
        int           schema_version;

        if (!split_schema_string(
                schema_name_and_version,
                &schema_name,
                &schema_version))
        {
            _error(ErrorStatus(
                ErrorStatus::MALFORMED_SCHEMA,
                string_printf(
                    "badly formed schema version string '%s'",
                    schema_name_and_version.c_str())));
            return any();
        }

        ErrorStatus error_status;
        if (SerializableObject* so = r._instance_from_schema(
                schema_name,
                schema_version,
                _dict,
                true /* internal_read */,
                &error_status))
        {
            if (!ref_id.empty())
            {
                resolver.object_for_id[ref_id] = so;
            }
            resolver.data_for_object.emplace(so, std::move(_dict));
            resolver.line_number_for_object[so] = _line_number;
            return any(SerializableObject::Retainer<>(so));
        }

        _error(error_status);
        return any();
    }
}

bool
SerializableObject::Reader::read(std::string const& key, bool* value)
{
    return _fetch(key, value);
}

bool
SerializableObject::Reader::read(std::string const& key, int* value)
{
    return _fetch(key, value);
}

bool
SerializableObject::Reader::read(std::string const& key, double* value)
{
    return _fetch(key, value);
}

bool
SerializableObject::Reader::read(std::string const& key, std::string* value)
{
    bool had_null;
    if (!_fetch(key, value, &had_null))
    {
        return false;
    }

    if (had_null)
    {
        value->clear();
    }
    return true;
}

bool
SerializableObject::Reader::read(std::string const& key, RationalTime* value)
{
    return _fetch(key, value);
}

bool
SerializableObject::Reader::read(std::string const& key, TimeRange* value)
{
    return _fetch(key, value);
}

bool
SerializableObject::Reader::read(std::string const& key, TimeTransform* value)
{
    return _fetch(key, value);
}

bool
SerializableObject::Reader::read(std::string const& key, AnyDictionary* value)
{
    return _fetch(key, value);
}

bool
SerializableObject::Reader::read(std::string const& key, AnyVector* value)
{
    return _fetch(key, value);
}

bool
SerializableObject::Reader::read(
    std::string const&    key,
    IMATH_NAMESPACE::V2d* value)
{
    return _fetch(key, value);
}

bool
SerializableObject::Reader::read(
    std::string const&      key,
    IMATH_NAMESPACE::Box2d* value)
{
    return _fetch(key, value);
}

template <typename T>
bool
SerializableObject::Reader::_read_optional(
    std::string const& key,
    optional<T>*       value)
{
    bool had_null;
    T    result;
    if (!SerializableObject::Reader::_fetch(key, &result, &had_null))
    {
        return false;
    }

    *value = had_null ? optional<T>() : optional<T>(result);
    return true;
}
bool
SerializableObject::Reader::read(std::string const& key, optional<bool>* value)
{
    return _read_optional(key, value);
}

bool
SerializableObject::Reader::read(std::string const& key, optional<int>* value)
{
    return _read_optional(key, value);
}

bool
SerializableObject::Reader::read(
    std::string const& key,
    optional<double>*  value)
{
    return _read_optional(key, value);
}

bool
SerializableObject::Reader::read(
    std::string const&      key,
    optional<RationalTime>* value)
{
    return _read_optional(key, value);
}

bool
SerializableObject::Reader::read(
    std::string const&   key,
    optional<TimeRange>* value)
{
    return _read_optional(key, value);
}

bool
SerializableObject::Reader::read(
    std::string const&       key,
    optional<TimeTransform>* value)
{
    return _read_optional(key, value);
}

bool
SerializableObject::Reader::read(
    std::string const&                key,
    optional<IMATH_NAMESPACE::Box2d>* value)
{
    return _read_optional(key, value);
}

bool
SerializableObject::Reader::read(std::string const& key, any* value)
{
    auto e = _dict.find(key);
    if (e == _dict.end())
    {
        _error(ErrorStatus(ErrorStatus::KEY_NOT_FOUND, key));
        return false;
    }
    else
    {
        value->swap(e->second);
        _dict.erase(e);
        return true;
    }
}

bool
deserialize_json_from_string(
    std::string const& input,
    any*               destination,
    ErrorStatus*       error_status)
{
    OTIO_rapidjson::Reader                            reader;
    OTIO_rapidjson::StringStream                      ss(input.c_str());
    OTIO_rapidjson::CursorStreamWrapper<decltype(ss)> csw(ss);
    JSONDecoder handler(std::bind(&decltype(csw)::GetLine, &csw));

    bool status =
        reader.Parse<OTIO_rapidjson::kParseNanAndInfFlag>(csw, handler);
    handler.finalize();

    if (handler.has_errored(error_status))
    {
        return false;
    }

    if (!status)
    {
        if (error_status)
        {
            auto msg      = GetParseError_En(reader.GetParseErrorCode());
            *error_status = ErrorStatus(
                ErrorStatus::JSON_PARSE_ERROR,
                string_printf(
                    "JSON parse error on input string: %s "
                    "(line %d, column %d)",
                    msg,
                    csw.GetLine(),
                    csw.GetColumn()));
        }
        return false;
    }

    destination->swap(handler._root);
    return true;
}

bool
deserialize_json_from_file(
    std::string const& file_name,
    any*               destination,
    ErrorStatus*       error_status)
{

    FILE* fp = nullptr;
#if defined(_WINDOWS)
    const int wlen =
        MultiByteToWideChar(CP_UTF8, 0, file_name.c_str(), -1, NULL, 0);
    std::vector<wchar_t> wchars(wlen);
    MultiByteToWideChar(CP_UTF8, 0, file_name.c_str(), -1, wchars.data(), wlen);
    if (_wfopen_s(&fp, wchars.data(), L"r") != 0)
    {
        fp = nullptr;
    }
#else  // _WINDOWS
    fp = fopen(file_name.c_str(), "r");
#endif // _WINDOWS
    if (!fp)
    {
        if (error_status)
        {
            *error_status =
                ErrorStatus(ErrorStatus::FILE_OPEN_FAILED, file_name);
        }
        return false;
    }

    OTIO_rapidjson::Reader reader;

    char                           readBuffer[65536];
    OTIO_rapidjson::FileReadStream fs(fp, readBuffer, sizeof(readBuffer));
    OTIO_rapidjson::CursorStreamWrapper<decltype(fs)> csw(fs);
    JSONDecoder handler(std::bind(&decltype(csw)::GetLine, &csw));

    bool status =
        reader.Parse<OTIO_rapidjson::kParseNanAndInfFlag>(csw, handler);
    fclose(fp);

    handler.finalize();

    if (handler.has_errored(error_status))
    {
        return false;
    }

    if (!status)
    {
        auto msg = GetParseError_En(reader.GetParseErrorCode());
        if (error_status)
        {
            *error_status = ErrorStatus(
                ErrorStatus::JSON_PARSE_ERROR,
                string_printf(
                    "JSON parse error on input string: %s "
                    "(line %d, column %d)",
                    msg,
                    csw.GetLine(),
                    csw.GetColumn()));
        }
        return false;
    }

    destination->swap(handler._root);
    return true;
}

}} // namespace opentimelineio::OPENTIMELINEIO_VERSION
