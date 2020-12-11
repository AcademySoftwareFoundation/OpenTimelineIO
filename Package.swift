// swift-tools-version:5.1
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "otio",

    products: [
        .library(name: "opentimelineio", targets: ["opentimelineio"])
    ],
    dependencies: [],
    targets: [
	// Not a "real" library: just header files needed C++ OTIO and
	// also exposed to clients using C++ OTIO.
        .target(name: "any",
		path: "src/deps",
		sources: ["spm-dummy/any.cpp"],
		publicHeadersPath: "."),

	// Not a "real" library: just header files needed C++ OTIO and
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
		cxxSettings: [CXXSetting.headerSearchPath("deps/rapidjson/include")])
    ],
    cxxLanguageStandard: CXXLanguageStandard.cxx11
)
