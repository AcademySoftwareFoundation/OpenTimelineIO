// swift-tools-version:5.3
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "OpenTimelineIO",
    platforms: [.macOS(.v10_13),
		.iOS(.v11)],
    products: [
        .library(name: "OpenTimelineIO_CXX", targets: ["OpenTimelineIO_CXX"]),
        .library(name: "OpenTime_CXX", targets: ["OpenTime_CXX"]),
        .library(name: "OpenTimelineIO", targets: ["OpenTimelineIO"])
    ],
    dependencies: [],
    targets: [
	// Not a "real" library: exposes any/any.hpp needed by OpenTimelineIO_CXX
	// and C++ clients of OpenTimelineIO_CXX.
        .target(name: "any",
		path: "src/spm-build/any/Sources",
		exclude: ["any/any.hpp"],
		sources: ["."],
		publicHeadersPath: "."),

	// Not a "real" library: exposes nonstd/optional.hpp needed by OpenTimelineIO_CXX
	// and C++ clients of OpenTimelineIO_CXX.
        .target(name: "optionallite",
		path: "src/spm-build/optional-lite/Sources",
		exclude: ["include/nonstd/optional.hpp"],
		sources: ["."],
		publicHeadersPath: "include"),

	// public target
        .target(name: "OpenTime_CXX",
		path: "src/spm-build/opentime/Sources",
		exclude: ["opentime/CMakeLists.txt"],
		sources: ["opentime"],
		publicHeadersPath: "."),

	// public target
        .target(name: "OpenTimelineIO_CXX",
		dependencies: ["OpenTime_CXX", "any", "optionallite"],
		path: "src/spm-build/opentimelineio/Sources",
		exclude: ["opentimelineio/main.cpp",
	      		  "opentimelineio/CMakeLists.txt"],
		sources: ["opentimelineio"],
		publicHeadersPath: ".",
		cxxSettings: [CXXSetting.headerSearchPath("../../rapidjson/include")]),

	.target(name: "OpenTimelineIO_objc",
		dependencies: ["OpenTimelineIO_CXX"],
		path: "./src/swift-opentimelineio/Sources",
		exclude: ["swift"],
		sources: ["objc"],
		publicHeadersPath: "objc/include"),

	// public target
	.target(name: "OpenTimelineIO",
		dependencies: ["OpenTimelineIO_objc"],
		path: "./src/swift-opentimelineio/Sources",
		exclude: ["objc"],
		sources: ["swift"]),

	.testTarget(name: "OpenTimelineIOTests",
                    dependencies: ["OpenTimelineIO"],
		    path: "./src/swift-opentimelineio/Tests",
		    sources: ["OpenTimelineIOTests"],
		    resources: [.process("data")])

    ],
    cxxLanguageStandard: CXXLanguageStandard.cxx11
)
