# Proposed Language Bridges

## Python

Since OTIO originated as Python (and has an extensive test suite, in Python), our starting position
is that existing Python code (adapters, plugins, schemadefs) must continue to work, as currently
written. Python code in the `core` or `schema` directories will of course be rewritten, but Python code
outside those modules should not be aware of any change.

The bridge from C++ to Python (and back) will be `pybind11`.  Given that existing code needs to work,
clearly, the bridge will be implemented so as to make the reflection of the C++ datastructures, back
to Python, utterly "Pythonic."  (It has to be, since we don't want to break existing code.)

Given the above, there's no point giving Python illustrations of how things will work going forward: they'll
work as they already have.

## Swift

The intention is to expose OTIO in Swift with the same care we take with Python: we want everything
to feel utterly Swift-like.  Because Swift can gain automatic API access to non-member
functions written in Objective-C++, and Objective-C++ can directly use the proposed OTIO C++ API,
we believe that a bridge to swift will not require writing
an explicit explicit `extern "C"` wrapper around OTIO C++.
We believe that like Python, Swift should be capable of defining new schemas,
and that access to existing and new schemas and their properties should
be done in terms of Swift API's that conform Swift's sequence/collection protocols,
just as Python interfaces do with respect to Python.

## Bridging to C (and other languages)

Briding to C (and by extension other languages) would presumably be accomplished
by writing an `extern "C"` wrapper around the OTIO C++ API.  This is of relatively
low priority, given that we will have three languages (C++ itself, Python, and Swift) that
do not need this.



