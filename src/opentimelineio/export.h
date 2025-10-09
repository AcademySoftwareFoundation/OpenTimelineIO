// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentime/export.h"

#if defined(OTIO_STATIC)
#   define OTIO_API
#   define OTIO_API_TYPE
#   define OTIO_API_TEMPLATE_CLASS(...)
#   define OTIO_API_TEMPLATE_STRUCT(...)
#   define OTIO_LOCAL
#else
#   if defined(OTIO_EXPORTS)
#       define OTIO_API OPENTIMELINIO_EXPORT
#       define OTIO_API_TYPE OPENTIMELINIO_EXPORT_TYPE
#        define OTIO_API_TEMPLATE_CLASS(...) \
            OPENTIMELINIO_EXPORT_TEMPLATE(class, __VA_ARGS__)
#        define OTIO_API_TEMPLATE_STRUCT(...) \
            OPENTIMELINIO_EXPORT_TEMPLATE(struct, __VA_ARGS__)
#   else
#       define OTIO_API OPENTIMELINIO_IMPORT
#       define OTIO_API_TYPE OPENTIMELINIO_IMPORT_TYPE
#       define OTIO_API_TEMPLATE_CLASS(...) \
            OPENTIMELINIO_IMPORT_TEMPLATE(class, __VA_ARGS__)
#       define OTIO_API_TEMPLATE_STRUCT(...) \
            OPENTIMELINIO_IMPORT_TEMPLATE(struct, __VA_ARGS__)
#   endif
#   define OTIO_LOCAL OPENTIMELINIO_HIDDEN
#endif
