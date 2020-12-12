// swift-tools-version:5.1
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "otio",
    platforms: [.iOS(.v13),
                 .macOS(.v10_13)],
    products: [
        .library(name: "Opentimelineio_CXX", targets: ["Opentimelineio_CXX"]),
        .library(name: "Opentimelineio", targets: ["Opentimelineio"])
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

        .target(name: "Opentimelineio_CXX",
		dependencies: ["opentime", "any", "optionallite"],
		path: "./src",
		exclude: ["opentimelineio/main.cpp"],
		sources: ["opentimelineio"],
		publicHeadersPath: ".",
		cxxSettings: [CXXSetting.headerSearchPath("deps/rapidjson/include")]),

	.target(name: "opentimelineio_objc",
		dependencies: ["Opentimelineio_CXX"],
		path: "./src/swift-opentimelineio",
		sources: ["Sources/objc"],
		publicHeadersPath: "Sources/objc/include"),

	.target(name: "Opentimelineio",
		dependencies: ["opentimelineio_objc"],
		path: "./src/swift-opentimelineio",
		sources: ["Sources/swift"])
    ],
    cxxLanguageStandard: CXXLanguageStandard.cxx11
)
