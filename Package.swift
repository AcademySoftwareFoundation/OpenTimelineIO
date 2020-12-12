// swift-tools-version:5.1
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "otio",
    platforms: [.iOS(.v13),
                 .macOS(.v10_13)],
    products: [
        .library(name: "opentimelineio", targets: ["opentimelineio"]),
        .library(name: "swift_opentimelineio", targets: ["swift_opentimelineio"])
    ],
    dependencies: [],
    targets: [
	// Not a "real" library: just header files needed by C++ OTIO and
	// also exposed to clients using C++ OTIO.
        .target(name: "any",
		path: "src/deps",
		sources: ["spm-dummy/any.cpp"],
		publicHeadersPath: "."),

	// Not a "real" library: just header files needed by C++ OTIO and
	// also exposed to clients using C++ OTIO.
        .target(name: "optionallite",
		path: "src/deps",
		sources: ["spm-dummy/optional.cpp"],
		publicHeadersPath: "optional-lite/include"),

        .target(name: "opentime",
		path: "./src/opentime",
		sources: ["."],
		publicHeadersPath: ".",
		cxxSettings: [CXXSetting.headerSearchPath("..")]),

        .target(name: "opentimelineio",
		dependencies: ["opentime", "any", "optionallite"],
		path: "./src",
		exclude: ["opentimelineio/main.cpp"],
		sources: ["opentimelineio"],
		publicHeadersPath: ".",
		cxxSettings: [CXXSetting.headerSearchPath("deps/rapidjson/include")]),

	.target(name: "objc_opentimelineio",
		dependencies: ["opentimelineio"],
		path: "./src/swift-opentimelineio",
		sources: ["objc"],
		publicHeadersPath: "objc/include"),

	.target(name: "swift_opentimelineio",
		dependencies: ["objc_opentimelineio"],
		path: "./src/swift-opentimelineio",
		sources: ["swift"])
    ],
    cxxLanguageStandard: CXXLanguageStandard.cxx11
)
