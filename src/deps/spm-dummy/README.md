Why is this directory here?
---------------------------

Some of the libraries that C++ OTIO depends on are header only libraries.
RapidJSON doesn't expose any header files to clients using the C++ OTIO libraries but
the `any' and `optional' header files need to be seen by clients compiling against C++ OTIO.

To do this, we package both as libraries, but Swift Package Manager (SPM) doesn't consider
something a valid library unless there's some source.  So we gratuitously add some dummy
C++ files, in this directory.

If you come across a way to let SPM function without the need for the dummy C++
files contained herein, please let us know!

