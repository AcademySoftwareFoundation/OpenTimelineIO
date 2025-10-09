// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#if defined(_WINDOWS)
#   if defined(__GNUC__) && __GNUC__ >= 4 || defined(__clang__)
#       define ARCH_EXPORT __attribute__((dllexport))
#       define ARCH_IMPORT __attribute__((dllimport))
#       define ARCH_HIDDEN
#       define ARCH_EXPORT_TYPE
#   else
#       define ARCH_EXPORT __declspec(dllexport)
#       define ARCH_IMPORT __declspec(dllimport)
#       define ARCH_HIDDEN
#       define ARCH_EXPORT_TYPE
#   endif
#elif defined(__GNUC__) && __GNUC__ >= 4 || defined(__clang__)
#   define ARCH_EXPORT __attribute__((visibility("default")))
#   define ARCH_IMPORT
#   define ARCH_HIDDEN __attribute__((visibility("hidden")))
#   if defined(__clang__)
#       define ARCH_EXPORT_TYPE __attribute__((type_visibility("default")))
#   else
#       define ARCH_EXPORT_TYPE __attribute__((visibility("default")))
#   endif
#else
#   define ARCH_EXPORT
#   define ARCH_IMPORT
#   define ARCH_HIDDEN
#   define ARCH_EXPORT_TYPE
#endif
#define ARCH_EXPORT_TEMPLATE(type, ...)
#define ARCH_IMPORT_TEMPLATE(type, ...) extern template type ARCH_IMPORT __VA_ARGS__

#if defined(OPENTIME_STATIC)
#   define OPENTIME_API
#   define OPENTIME_API_TYPE
#   define OPENTIME_API_TEMPLATE_CLASS(...)
#   define OPENTIME_API_TEMPLATE_STRUCT(...)
#   define OPENTIME_LOCAL
#else
#   if defined(OPENTIME_EXPORTS)
#       define OPENTIME_API ARCH_EXPORT
#       define OPENTIME_API_TYPE ARCH_EXPORT_TYPE
#       define OPENTIME_API_TEMPLATE_CLASS(...) ARCH_EXPORT_TEMPLATE(class, __VA_ARGS__)
#       define OPENTIME_API_TEMPLATE_STRUCT(...) ARCH_EXPORT_TEMPLATE(struct, __VA_ARGS__)
#   else
#       define OPENTIME_API ARCH_IMPORT
#       define OPENTIME_API_TYPE ARCH_IMPORT_TYPE
#       define OPENTIME_API_TEMPLATE_CLASS(...) ARCH_IMPORT_TEMPLATE(class, __VA_ARGS__)
#       define OPENTIME_API_TEMPLATE_STRUCT(...) ARCH_IMPORT_TEMPLATE(struct, __VA_ARGS__)
#   endif
#   define OPENTIME_LOCAL ARCH_HIDDEN
#endif
