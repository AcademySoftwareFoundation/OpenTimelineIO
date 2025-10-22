// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

// For an explanation of how these export defines work, see:
// https://github.com/PixarAnimationStudios/OpenUSD/blob/dev/pxr/base/arch/export.h
#if defined(_WINDOWS)
#   if defined(__GNUC__) && __GNUC__ >= 4 || defined(__clang__)
#       define OPENTIMELINIO_EXPORT __attribute__((dllexport))
#       define OPENTIMELINIO_IMPORT __attribute__((dllimport))
#       define OPENTIMELINIO_HIDDEN
#       define OPENTIMELINIO_EXPORT_TYPE
#   else
#       define OPENTIMELINIO_EXPORT __declspec(dllexport)
#       define OPENTIMELINIO_IMPORT __declspec(dllimport)
#       define OPENTIMELINIO_HIDDEN
#       define OPENTIMELINIO_EXPORT_TYPE
#   endif
#elif defined(__GNUC__) && __GNUC__ >= 4 || defined(__clang__)
#   define OPENTIMELINIO_EXPORT __attribute__((visibility("default")))
#   define OPENTIMELINIO_IMPORT
#   define OPENTIMELINIO_HIDDEN __attribute__((visibility("hidden")))
#   if defined(__clang__)
#       define OPENTIMELINIO_EXPORT_TYPE __attribute__((type_visibility("default")))
#   else
#       define OPENTIMELINIO_EXPORT_TYPE __attribute__((visibility("default")))
#   endif
#else
#   define OPENTIMELINIO_EXPORT
#   define OPENTIMELINIO_IMPORT
#   define OPENTIMELINIO_HIDDEN
#   define OPENTIMELINIO_EXPORT_TYPE
#endif
#define OPENTIMELINIO_EXPORT_TEMPLATE(type, ...)
#define OPENTIMELINIO_IMPORT_TEMPLATE(type, ...) \
    extern template type OPENTIMELINIO_IMPORT __VA_ARGS__

#if defined(OPENTIME_STATIC)
#   define OPENTIME_API
#   define OPENTIME_API_TYPE
#   define OPENTIME_API_TEMPLATE_CLASS(...)
#   define OPENTIME_API_TEMPLATE_STRUCT(...)
#   define OPENTIME_LOCAL
#else
#   if defined(OPENTIME_EXPORTS)
#       define OPENTIME_API OPENTIMELINIO_EXPORT
#       define OPENTIME_API_TYPE OPENTIMELINIO_EXPORT_TYPE
#       define OPENTIME_API_TEMPLATE_CLASS(...) \
            OPENTIMELINIO_EXPORT_TEMPLATE(class, __VA_ARGS__)
#       define OPENTIME_API_TEMPLATE_STRUCT(...) \
            OPENTIMELINIO_EXPORT_TEMPLATE(struct, __VA_ARGS__)
#   else
#       define OPENTIME_API OPENTIMELINIO_IMPORT
#       define OPENTIME_API_TYPE OPENTIMELINIO_IMPORT_TYPE
#       define OPENTIME_API_TEMPLATE_CLASS(...) \
            OPENTIMELINIO_IMPORT_TEMPLATE(class, __VA_ARGS__)
#       define OPENTIME_API_TEMPLATE_STRUCT(...) \
            OPENTIMELINIO_IMPORT_TEMPLATE(struct, __VA_ARGS__)
#   endif
#   define OPENTIME_LOCAL OPENTIMELINIO_HIDDEN
#endif
