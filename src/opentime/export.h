// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

// For an explanation of how these export defines work, see:
// https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/pxr/base/arch/export.h
#if defined(_WINDOWS)
#   if defined(__GNUC__) && __GNUC__ >= 4 || defined(__clang__)
#       define OPENTIMELINEIO_EXPORT __attribute__((dllexport))
#       define OPENTIMELINEIO_IMPORT __attribute__((dllimport))
#       define OPENTIMELINEIO_HIDDEN
#       define OPENTIMELINEIO_EXPORT_TYPE
#       define OPENTIMELINEIO_IMPORT_TYPE
#   else
#       define OPENTIMELINEIO_EXPORT __declspec(dllexport)
#       define OPENTIMELINEIO_IMPORT __declspec(dllimport)
#       define OPENTIMELINEIO_HIDDEN
#       define OPENTIMELINEIO_EXPORT_TYPE
#       define OPENTIMELINEIO_IMPORT_TYPE
#   endif
#elif defined(__GNUC__) && __GNUC__ >= 4 || defined(__clang__)
#   define OPENTIMELINEIO_EXPORT __attribute__((visibility("default")))
#   define OPENTIMELINEIO_IMPORT
#   define OPENTIMELINEIO_HIDDEN __attribute__((visibility("hidden")))
#   if defined(__clang__)
#       define OPENTIMELINEIO_EXPORT_TYPE __attribute__((type_visibility("default")))
#   else
#       define OPENTIMELINEIO_EXPORT_TYPE __attribute__((visibility("default")))
#   endif
#   define OPENTIMELINEIO_IMPORT_TYPE
#else
#   define OPENTIMELINEIO_EXPORT
#   define OPENTIMELINEIO_IMPORT
#   define OPENTIMELINEIO_HIDDEN
#   define OPENTIMELINEIO_EXPORT_TYPE
#   define OPENTIMELINEIO_IMPORT_TYPE
#endif
#define OPENTIMELINEIO_EXPORT_TEMPLATE(type, ...)
#define OPENTIMELINEIO_IMPORT_TEMPLATE(type, ...) \
    extern template type OPENTIMELINEIO_IMPORT __VA_ARGS__

#if defined(OPENTIME_STATIC)
#   define OPENTIME_API
#   define OPENTIME_API_TYPE
#   define OPENTIME_API_TEMPLATE_CLASS(...)
#   define OPENTIME_API_TEMPLATE_STRUCT(...)
#   define OPENTIME_LOCAL
#else
#   if defined(OPENTIME_EXPORTS)
#       define OPENTIME_API OPENTIMELINEIO_EXPORT
#       define OPENTIME_API_TYPE OPENTIMELINEIO_EXPORT_TYPE
#       define OPENTIME_API_TEMPLATE_CLASS(...) \
            OPENTIMELINEIO_EXPORT_TEMPLATE(class, __VA_ARGS__)
#       define OPENTIME_API_TEMPLATE_STRUCT(...) \
            OPENTIMELINEIO_EXPORT_TEMPLATE(struct, __VA_ARGS__)
#   else
#       define OPENTIME_API OPENTIMELINEIO_IMPORT
#       define OPENTIME_API_TYPE OPENTIMELINEIO_IMPORT_TYPE
#       define OPENTIME_API_TEMPLATE_CLASS(...) \
            OPENTIMELINEIO_IMPORT_TEMPLATE(class, __VA_ARGS__)
#       define OPENTIME_API_TEMPLATE_STRUCT(...) \
            OPENTIMELINEIO_IMPORT_TEMPLATE(struct, __VA_ARGS__)
#   endif
#   define OPENTIME_LOCAL OPENTIMELINEIO_HIDDEN
#endif
