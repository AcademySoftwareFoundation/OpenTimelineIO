// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include "otio_errorStatusHandler.h"

#include <opentimelineio/bundle.h>
#include <opentimelineio/bundleUtils.h>

using namespace opentimelineio::OPENTIMELINEIO_VERSION;
using namespace opentimelineio::OPENTIMELINEIO_VERSION::bundle;

namespace py = pybind11;

void otio_bundle_bindings(pybind11::module m)
{
    auto mbundle = m.def_submodule("bundle");
    
    mbundle.attr("otioz_version") = otioz_version;
    mbundle.attr("otiod_version") = otiod_version;
    mbundle.attr("version_file") = version_file;
    mbundle.attr("otio_file") = otio_file;
    mbundle.attr("media_dir") = media_dir;
    
    py::enum_<MediaReferencePolicy>(mbundle, "MediaReferencePolicy",
R"docstring(
This enumeration provides the bundle media reference policy.
)docstring")
        .value(
            "ErrorIfNotFile",
            MediaReferencePolicy::ErrorIfNotFile,
            "Return an error if there are any non-file media references.")
        .value(
            "MissingIfNotFile",
            MediaReferencePolicy::MissingIfNotFile,
            "Replace non-file media references with missing references.")
        .value(
            "AllMissing",
            MediaReferencePolicy::AllMissing,
            "Replace all media references with missing references.");
    
    py::class_<WriteOptions>(mbundle, "WriteOptions",
R"docstring(
Options for writing bundles.
)docstring")
        .def(py::init<>())
        .def_readwrite(
            "parent_path",
            &WriteOptions::parent_path,
            "The parent path is used to locate media with relative paths. If "
            "parent path is empty, paths are relative to the current working "
            "directory.")
        .def_readwrite(
            "media_policy",
            &WriteOptions::media_policy,
            "The bundle media reference policy.")
        .def_readwrite(
            "indent",
            &WriteOptions::indent,
            "The number of spaces to use for JSON indentation.");

    py::class_<OtiozReadOptions>(mbundle, "OtiozReadOptions",
R"docstring(
Options for reading .otioz bundles.
)docstring")
        .def(py::init<>())
        .def_readwrite(
            "extract_path",
            &OtiozReadOptions::extract_path,
            "Extract the contents of the bundle to the given path. If the path "
            "is empty, the contents are not extracted, and only the timeline "
            "is read from the bundle.");

    py::class_<OtiodReadOptions>(mbundle, "OtiodReadOptions",
R"docstring(
Options for reading .otiod bundles.
)docstring")
        .def(py::init<>())
        .def_readwrite(
            "absolute_media_reference_paths",
            &OtiodReadOptions::absolute_media_reference_paths,
            "Use absolute paths for media references.");

    mbundle.def(
        "get_media_size",
        [](
            Timeline const*     timeline,
            WriteOptions const& options = WriteOptions())
        {
            return get_media_size(timeline, options, ErrorStatusHandler());
        },
        "Get the total size (in bytes) of the media files that will be put "
        "into the bundle.",
        py::arg("timeline"),
        py::arg("options") = WriteOptions());

    mbundle.def(
        "to_otioz",
        [](
            Timeline const*     timeline,
            std::string const&  file_name,
            WriteOptions const& options = WriteOptions())
        {
            return to_otioz(timeline, file_name, options, ErrorStatusHandler());
        },
        "Write a timeline and it's referenced media to an .otioz bundle.",
        py::arg("timeline"),
        py::arg("file_name"),
        py::arg("options") = WriteOptions());

    mbundle.def(
        "from_otioz",
        [](
            std::string const&      file_name,
            OtiozReadOptions const& options = OtiozReadOptions())
        {
            return from_otioz(file_name, options, ErrorStatusHandler());
        },
        "Read a timeline from an .otioz bundle.",
        py::arg("file_name"),
        py::arg("options") = OtiozReadOptions());

    mbundle.def(
        "to_otiod",
        [](
            Timeline const*     timeline,
            std::string const&  file_name,
            WriteOptions const& options = WriteOptions())
        {
            return to_otiod(timeline, file_name, options, ErrorStatusHandler());
        },
        "Write a timeline and it's referenced media to an .otiod bundle.",
        py::arg("timeline"),
        py::arg("file_name"),
        py::arg("options") = WriteOptions());

    mbundle.def(
        "from_otiod",
        [](
            std::string const&      file_name,
            OtiodReadOptions const& options = OtiodReadOptions())
        {
            return from_otiod(file_name, options, ErrorStatusHandler());
        },
        "Read a timeline from an .otiod bundle.",
        py::arg("file_name"),
        py::arg("options") = OtiodReadOptions());
}
