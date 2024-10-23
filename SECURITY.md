<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright Contributors to the OpenTimelineIO project -->

# Security Policy

## Reporting a Vulnerability

If you think you've found a potential vulnerability in OpenTimelineIO, please
report it by filing a GitHub [security
advisory](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/security/advisories/new). Alternatively, email
[security@opentimeline.io](mailto:security@opentimeline.io?subject=OpenTimelineIO%20Vulnerability%20Report&body=Impact%0A_What%20is%20it,%20who%20is%20impacted_%0A%0APatches%0A_Has%20it%20been%20patched%20and%20in%20which%20version_%0A%0AWorkarounds%0A_Is%20there%20a%20way%20for%20users%20to%20fix%20or%20remediate%20without%20upgrading_%0A%0AReferences%0A_Where%20can%20users%20visit%20to%20find%20out%20more_)
and provide your contact info for further private/secure discussion.  If your email does not receive a prompt
acknowledgement, your address may be blocked.

Our policy is to acknowledge the receipt of vulnerability reports
within 48 hours. Our policy is to address critical security vulnerabilities
rapidly and post patches within 14 days if possible.

## Known Vulnerabilities

These vulnerabilities are present in the given versions:

* No known vulnerabilities

See the [release notes](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/releases) for more information.

## Supported Versions

This gives guidance about which branches are supported with patches to
security vulnerabilities.

| Version / branch | Supported                                                                                                                          |
|------------------|------------------------------------------------------------------------------------------------------------------------------------|
| main             | :white_check_mark: :construction: ALL fixes immediately, but this is a branch under development and may be unstable in other ways. |
| 0.17.0           | :white_check_mark: All fixes that can be backported without breaking compatibility.                                            |
| 0.16.x           | :warning: Only the most critical fixes, only if they can be easily backported.                                                     |
| <= 0.15.x        | :x: No longer receiving patches of any kind.                                                                                       |

  
### Software Dependencies

OpenTimelineIO depends on:

- [Imath](https://github.com/AcademySoftwareFoundation/Imath) - Provides Vector, Matrix, and Bounding Box primitives. 

- [pybind11](https://github.com/pybind/pybind11) (only if built with Python bindings) - Used to create Python bindings for the C++ library.

- [rapidjson](https://github.com/Tencent/rapidjson/) - Used in serialization/deserialization of the `.otio` JSON file format.
