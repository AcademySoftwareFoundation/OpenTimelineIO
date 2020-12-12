CLI Swift Package Manager Example
=================================

If you copy/download `examples/swift-package-manager` (`examples` is a top-level folder of this repository)
you can play around with some simple CLI samples that show off building with SPM.

For example, put a copy of `examples/swift-package-manager` in /home/some-user, and then:

Then:
```
    $ cd /home/some-user/swift-package-manager
    $ swift build
    (output)

    $ .build/debug/cxx_example
    (output)

    $ .build/debug/swift_example
    (output)
```
    
Opentimeineio Swift Test Suite
=================================

You can also build and test the Swift portion of the Opentimelineio repository
(which requires building the C++ core library, but nothing having to do with python or any other
language) from the command line easily as well:
```
    $ git clone https://github.com/davidbaraff/OpenTimelineIO.git --recurse-submodules
    (output)

    $ cd Opentimelineio
    $ git checkout spm  # skip this once the PR is closed
    $ swift build	    # optional: swift test will do a build anyway, as needed
    (output)

    $ swift test
    (output)
    Test Suite 'testTransform' passed at 2020-12-12 15:02:15.593.
             Executed 5 tests, with 0 failures (0 unexpected) in 0.001 (0.001) seconds
    Test Suite 'otioPackageTests.xctest' passed at 2020-12-12 15:02:15.593.
             Executed 56 tests, with 0 failures (0 unexpected) in 2.037 (2.039) seconds
    Test Suite 'All tests' passed at 2020-12-12 15:02:15.593.
             Executed 56 tests, with 0 failures (0 unexpected) in 2.037 (2.039) seconds
```	     
	 
Xcode
=====
Simply use the Package Manager in Xcode and bring in
  `https://github.com/davidbaraff/OpenTimelineIO.git` with branch set to `spm`.

You should see a choice of two products that can be added to your project/wrkspace:
`Opentimelineio_CXX` is the C++ build of Opentimelineio
if you wish to do C++ development; otherwise, for Swift/Objective-C work, choose `Opentimelineio`.




