# Writing OTIO in C, C++ or Python (June 2018)

Here are some initial thoughts about the subject, from around June 2018,
about providing languages other than Python.  The actual current
plan is [here](./cxx).

The current python implementation of OTIO has been super helpful for defining the library and getting studio needs settled, but in order to integrate the library into vendor tools, a C/C++ implementation is required.  We don't want to give up the Python API, however, so the plan is to port the library to C/C++ with a Python wrapper that implements an interface to the library as it currently stands; existing Python code shouldn't notice the switch.  We can use the existing unit tests to vet the implementation and make sure that it matches the Python API.

There are several options for how to wrap C/C++ in Python, the intent of this document is to discuss the options we see and their pros/cons.

## Python C-API

link: [Python C-API](https://docs.python.org/2/c-api/index.html)

Pros:

* No extra dependencies

Cons:

* Extremely boilerplate heavy
* Have to manually build every part of the binding
* For users of boost, the bindings won't be directly compatible with boost bindings. 
* Error prone: less type-safe and the reference counting must be manually done

## Boost-Python

link: [Boost-python](http://www.boost.org/doc/libs/1_64_0/libs/python/doc/html/index.html)

Pros:

* High level binding
* Established, familiarity around the industry, reasonably popular

Cons:

* Heavy dependency to add to projects if they aren't already using boost
 
## PyBind11

link: [PyBind11 Github](https://github.com/pybind/pybind11)

Pros:

* High level binding
* Takes advantage of C++11/17 features to make wrapping even more terse (if they're available)
* Can be embedded in the project without requiring Boost

Cons:

* For users of boost, the bindings won't be directly compatible with boost bindings.
* Newer and less established than other options.

## Conclusion

After talking with several vendors, studios, and participants, we have concluded that we will make this:

* C++ Implementation of OTIO (following VFX Platform CY2017 standard C++11)
* Pybind11 Bindings
* To support other languages will make a `extern "C"` wrapper around the C++ API
* Support for Swift (with some bridging provided by NSObject derived classes written in Objective-C++)

This will replace the current pure-Python implementation, attempting to match the current Python API as much as possible, so that existing Python programs that use OTIO should not need to be modified to make the switch.

We will try to make this a smooth transition, by starting with `opentime` and working out to the rest of the API.

Also, in the future, we will likely provide Boost Python bindings to the C++ API for applications that already use Boost Python.

