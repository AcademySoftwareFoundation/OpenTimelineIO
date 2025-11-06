// SPDX-License-Identifier: Apache-2.0
// Copyright Contributors to the OpenTimelineIO project

#pragma once

#include "opentime/export.h"

#if defined(OTIO_STATIC)
#    define OTIO_API
#    define OTIO_API_TYPE
#    define OTIO_API_TEMPLATE_CLASS(...)
#    define OTIO_API_TEMPLATE_STRUCT(...)
#    define OTIO_LOCAL
#else
#    if defined(OTIO_EXPORTS)
#        define OTIO_API OPENTIMELINEIO_EXPORT
#        define OTIO_API_TYPE OPENTIMELINEIO_EXPORT_TYPE
#        define OTIO_API_TEMPLATE_CLASS(...)                                   \
            OPENTIMELINEIO_EXPORT_TEMPLATE(class, __VA_ARGS__)
#        define OTIO_API_TEMPLATE_STRUCT(...)                                  \
            OPENTIMELINEIO_EXPORT_TEMPLATE(struct, __VA_ARGS__)
#    else
#        define OTIO_API OPENTIMELINEIO_IMPORT
#        define OTIO_API_TYPE OPENTIMELINEIO_IMPORT_TYPE
#        define OTIO_API_TEMPLATE_CLASS(...)                                   \
            OPENTIMELINEIO_IMPORT_TEMPLATE(class, __VA_ARGS__)
#        define OTIO_API_TEMPLATE_STRUCT(...)                                  \
            OPENTIMELINEIO_IMPORT_TEMPLATE(struct, __VA_ARGS__)
#    endif
#    define OTIO_LOCAL OPENTIMELINEIO_HIDDEN
#endif
