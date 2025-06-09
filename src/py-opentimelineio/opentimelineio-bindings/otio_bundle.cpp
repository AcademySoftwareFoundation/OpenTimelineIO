// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include "otio_errorStatusHandler.h"

#include <opentimelineio/bundle.h>

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
    
    py::class_<ToBundleOptions>(mbundle, "ToBundleOptions",
R"docstring(
Options for writing bundles.
)docstring")
        .def(py::init<>())
        .def_readwrite(
            "parent_path",
            &ToBundleOptions::parent_path,
            "The parent path is used to locate media with relative paths. If "
            "parent path is empty, paths are relative to the current working "
            "directory.")
        .def_readwrite(
            "media_reference_policy",
            &ToBundleOptions::media_reference_policy,
            "The bundle media reference policy.")
        .def_readwrite(
            "indent",
            &ToBundleOptions::indent,
            "The number of spaces to use for JSON indentation.");
    
    mbundle.def(
        "get_media_size",
        [](
            Timeline const*        timeline,
            ToBundleOptions const& options = ToBundleOptions())
        {
            return get_media_size(timeline, options, ErrorStatusHandler());
        },
        "Get the total size (in bytes) of the media files that will be put "
        "into the bundle.",
        py::arg("timeline"),
        py::arg("options") = ToBundleOptions());

    mbundle.def(
        "to_otioz",
        [](
            Timeline const*        timeline,
            std::string const&     file_name,
            ToBundleOptions const& options = ToBundleOptions())
        {
            return to_otioz(timeline, file_name, options, ErrorStatusHandler());
        },
        "Write a timeline and it's referenced media to an .otioz bundle.",
        py::arg("timeline"),
        py::arg("file_name"),
        py::arg("options") = ToBundleOptions());

    py::class_<FromOtiozOptions>(mbundle, "FromOtiozOptions",
R"docstring(
Options for reading .otioz bundles.
)docstring")
        .def(py::init<>())
        .def_readwrite(
            "extract_path",
            &FromOtiozOptions::extract_path,
            "Extract the contents of the bundle to the given path. If the path "
            "is empty, the contents are not extracted, and only the timeline "
            "is read from the bundle.");

    mbundle.def(
        "from_otioz",
        [](
            std::string const&      file_name,
            FromOtiozOptions const& options = FromOtiozOptions())
        {
            return from_otioz(file_name, options, ErrorStatusHandler());
        },
        "Read a timeline from an .otioz bundle.",
        py::arg("file_name"),
        py::arg("options") = FromOtiozOptions());

    mbundle.def(
        "to_otiod",
        [](
            Timeline const*        timeline,
            std::string const&     file_name,
            ToBundleOptions const& options = ToBundleOptions())
        {
            return to_otiod(timeline, file_name, options, ErrorStatusHandler());
        },
        "Write a timeline and it's referenced media to an .otiod bundle.",
        py::arg("timeline"),
        py::arg("file_name"),
        py::arg("options") = ToBundleOptions());

    py::class_<FromOtiodOptions>(mbundle, "FromOtiodOptions",
R"docstring(
Options for reading .otiod bundles.
)docstring")
        .def(py::init<>())
        .def_readwrite(
            "absolute_media_reference_paths",
            &FromOtiodOptions::absolute_media_reference_paths,
            "Use absolute paths for media references.");

    mbundle.def(
        "from_otiod",
        [](
            std::string const&      file_name,
            FromOtiodOptions const& options = FromOtiodOptions())
        {
            return from_otiod(file_name, options, ErrorStatusHandler());
        },
        "Read a timeline from an .otiod bundle.",
        py::arg("file_name"),
        py::arg("options") = FromOtiodOptions());
}
