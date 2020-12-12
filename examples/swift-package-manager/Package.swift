// swift-tools-version:5.1
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "otio_examples",

    platforms: [.iOS(.v13),
                .macOS(.v10_13)],

    dependencies: [
        .package(url: "https://github.com/davidbaraff/OpenTimelineIO.git", .branch("spm"))
    ],

    targets: [
	.target(name: "cxx_example",
                dependencies: ["Opentimelineio_CXX"]),

	.target(name: "swift_example",
                dependencies: ["Opentimelineio"])
    ],

    cxxLanguageStandard: CXXLanguageStandard.cxx11    
)
