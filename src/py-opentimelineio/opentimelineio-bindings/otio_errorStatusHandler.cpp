#include "otio_errorStatusHandler.h"

namespace pybind11 {
    PYBIND11_RUNTIME_EXCEPTION(not_implemented_error, PyExc_NotImplementedError)
}
    
ErrorStatusHandler::~ErrorStatusHandler() noexcept(false) {
    namespace py = pybind11;
    if (!error_status) {
        return;
    }
    
    switch(error_status.outcome) {
    case ErrorStatus::NOT_IMPLEMENTED:
        throw py::not_implemented_error();
    case ErrorStatus::ILLEGAL_INDEX:
        throw py::index_error();
    case ErrorStatus::KEY_NOT_FOUND:
        throw py::key_error(error_status.details);
    case ErrorStatus::INTERNAL_ERROR:
        throw py::value_error(std::string("Internal error (aka \"this is a bug\"):" ) + error_status.details);
    case ErrorStatus::UNRESOLVED_OBJECT_REFERENCE:
        throw py::value_error("Unresolved object reference while reading: " + error_status.details);
    case ErrorStatus::DUPLICATE_OBJECT_REFERENCE:
        throw py::value_error("Duplicated object reference while reading: " + error_status.details);
    case ErrorStatus::MALFORMED_SCHEMA:
        throw py::value_error("Illegal/malformed schema: " + error_status.details);
    case ErrorStatus::JSON_PARSE_ERROR:
        throw py::value_error("JSON parse error while reading: " + error_status.details);
    case ErrorStatus::FILE_OPEN_FAILED:
        throw py::value_error("failed to open file for reading: " + error_status.details);
    case ErrorStatus::FILE_WRITE_FAILED:
        throw py::value_error("failed to open file for writing: " + error_status.details);
    default:
        throw py::value_error(error_status.details);
    }
}
