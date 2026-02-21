// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include "otio_errorStatusHandler.h"
#include "opentimelineio/stringUtils.h"
#include "opentimelineio/serializableObject.h"

namespace pybind11 {
    PYBIND11_RUNTIME_EXCEPTION(not_implemented_error, PyExc_NotImplementedError)
}

namespace py = pybind11;

struct OTIOException : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

struct _NotAChildException : public OTIOException {
    using  OTIOException::OTIOException;
};

struct _UnsupportedSchemaException : public OTIOException {
    using  OTIOException::OTIOException;
};

struct _CannotComputeAvailableRangeException : public OTIOException {
    using  OTIOException::OTIOException;
};

struct _BundleSizeException : public OTIOException {
    using  OTIOException::OTIOException;
};

struct _BundleWriteException : public OTIOException {
    using  OTIOException::OTIOException;
};

struct _BundleReadException : public OTIOException {
    using  OTIOException::OTIOException;
};

ErrorStatusHandler::~ErrorStatusHandler() noexcept(false) {
    if (!is_error(error_status)) {
        return;
    }

    switch(error_status.outcome) {
    case ErrorStatus::NOT_IMPLEMENTED:
        throw py::not_implemented_error(error_status.details);
    case ErrorStatus::ILLEGAL_INDEX:
        throw py::index_error(error_status.details);
    case ErrorStatus::KEY_NOT_FOUND:
        throw py::key_error(error_status.details);
    case ErrorStatus::INTERNAL_ERROR:
        throw py::value_error(std::string("Internal error (aka \"this is a bug\"):" ) + details());
    case ErrorStatus::UNRESOLVED_OBJECT_REFERENCE:
        throw py::value_error("Unresolved object reference while reading: " + details());
    case ErrorStatus::DUPLICATE_OBJECT_REFERENCE:
        throw py::value_error("Duplicated object reference while reading: " + details());
    case ErrorStatus::MALFORMED_SCHEMA:
        throw py::value_error("Illegal/malformed schema: " + details());
    case ErrorStatus::JSON_PARSE_ERROR:
        throw py::value_error("JSON parse error while reading: " + details());
    case ErrorStatus::FILE_OPEN_FAILED:
        PyErr_SetFromErrnoWithFilename(PyExc_OSError, details().c_str());
        throw py::error_already_set();
    case ErrorStatus::FILE_WRITE_FAILED:
        PyErr_SetFromErrnoWithFilename(PyExc_OSError, details().c_str());
        throw py::error_already_set();
    case ErrorStatus::SCHEMA_VERSION_UNSUPPORTED:
        throw _UnsupportedSchemaException(full_details());
    case ErrorStatus::NOT_A_CHILD_OF:
    case ErrorStatus::NOT_A_CHILD:
    case ErrorStatus::NOT_DESCENDED_FROM:
        throw _NotAChildException(full_details());
    case ErrorStatus::CANNOT_COMPUTE_AVAILABLE_RANGE:
        throw _CannotComputeAvailableRangeException(full_details());
    case ErrorStatus::OBJECT_CYCLE:
        throw py::value_error("Detected SerializableObject cycle while copying/serializing: " + details());
    case ErrorStatus::MEDIA_REFERENCES_DO_NOT_CONTAIN_ACTIVE_KEY:
        throw py::value_error("The media references do not contain the active key");
    case ErrorStatus::MEDIA_REFERENCES_CONTAIN_EMPTY_KEY:
        throw py::value_error("The media references contain an empty key");
    case ErrorStatus::BUNDLE_SIZE_ERROR:
        throw _BundleSizeException(full_details());
    case ErrorStatus::BUNDLE_WRITE_ERROR:
        throw _BundleWriteException(full_details());
    case ErrorStatus::BUNDLE_READ_ERROR:
        throw _BundleReadException(full_details());
    default:
        throw py::value_error(full_details());
    }
}

std::string ErrorStatusHandler::details() {
    if (!error_status.object_details) {
        return error_status.details;
    }

    std::string object_str = py::cast<std::string>(py::str(py::cast(error_status.object_details)));
    return string_printf("%s: %s", error_status.details.c_str(),
                         object_str.c_str());
}

std::string ErrorStatusHandler::full_details() {
    if (!error_status.object_details) {
        return error_status.full_description;
    }

    std::string object_str = py::cast<std::string>(py::str(py::cast(error_status.object_details)));
    return string_printf("%s: %s", error_status.full_description.c_str(),
                         object_str.c_str());
}

void otio_exception_bindings(py::module m) {
    auto otio_exception = py::register_exception<OTIOException>(m, "OTIOError");
    py::register_exception<_NotAChildException>(m, "NotAChildError", otio_exception.ptr());
    py::register_exception<_UnsupportedSchemaException>(m, "UnsupportedSchemaError", otio_exception.ptr());
    py::register_exception<_CannotComputeAvailableRangeException>(m, "CannotComputeAvailableRangeError", otio_exception.ptr());
}
