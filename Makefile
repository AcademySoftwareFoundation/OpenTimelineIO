.PHONY: coverage test test_first_fail clean autopep8 lint doc-html \
	python-version wheel manifest lcov

# Special definition to handle Make from stripping newlines
define newline


endef

# Color highlighting for the shell
ccred = $(shell echo "\033[0;31m")
ccgreen = $(shell echo "\033[0;32m")
ccblue = $(shell echo "\033[0;34m")
ccend = $(shell echo "\033[0m")

# Helpful link to install development dependencies declared in setup.py
define dev_deps_message
$(ccred)You can install this and other development dependencies with$(newline)$(ccend)\
$(ccblue)	pip install -e .[dev]$(newline)$(ccend)
endef

# variables
MAKE_PROG ?= make

# external programs
COV_PROG := $(shell command -v coverage 2> /dev/null)
LCOV_PROG := $(shell command -v lcov 2> /dev/null)
PYCODESTYLE_PROG := $(shell command -v pycodestyle 2> /dev/null)
PYFLAKES_PROG := $(shell command -v pyflakes 2> /dev/null)
FLAKE8_PROG := $(shell command -v flake8 2> /dev/null)
CHECK_MANIFEST_PROG := $(shell command -v check-manifest 2> /dev/null)
CLANG_FORMAT_PROG := $(shell command -v clang-format 2> /dev/null)
# AUTOPEP8_PROG := $(shell command -v autopep8 2> /dev/null)
TEST_ARGS=

GIT = git
GITSTATUS := $(shell git diff-index --quiet HEAD . 1>&2 2> /dev/null; echo $$?)


ifeq ($(VERBOSE), 1)
	TEST_ARGS:=-v
endif

# Clear the environment of a preset media linker
OTIO_DEFAULT_MEDIA_LINKER =


# run all the unit tests
test: test-core test-contrib

test-core: python-version
	@echo "$(ccgreen)Running Core tests...$(ccend)"
	@python -m unittest discover -s tests $(TEST_ARGS)

test-contrib: python-version
	@echo "$(ccgreen)Running Contrib tests...$(ccend)"
	@${MAKE_PROG} -C contrib/opentimelineio_contrib/adapters test VERBOSE=$(VERBOSE)

# CI
###################################
ci-prebuild: manifest lint
ci-postbuild: coverage
###################################

python-version:
	@python --version

coverage: coverage-core coverage-contrib coverage-report

coverage-report:
	@${COV_PROG} combine .coverage* contrib/opentimelineio_contrib/adapters/.coverage*
	@${COV_PROG} xml
	@${COV_PROG} report -m

# NOTE: coverage configuration is done in setup.cfg

coverage-core: python-version
ifndef COV_PROG
	$(error $(newline)$(ccred) Coverage is not available please see:$(newline)$(ccend)\
	$(ccblue)	https://coverage.readthedocs.io/en/coverage-4.2/install.html $(newline)$(ccend)\
	$(dev_deps_message))
endif
	@${COV_PROG} run -p -m unittest discover tests

coverage-contrib: python-version
	@${MAKE_PROG} -C contrib/opentimelineio_contrib/adapters coverage VERBOSE=$(VERBOSE)

lcov: 
ifndef LCOV_PROG
	$(error $(newline)$(ccred) lcov is not available please see:$(newline)$(ccend)\
	$(ccblue)	https://github.com/linux-test-project/lcov/blob/master/README $(ccend))
endif
ifneq (OTIO_CXX_COVERAGE_BUILD, 'ON')
	$(warning $(newline)Warning: unless compiled with \
		OTIO_CXX_COVERAGE_BUILD="ON", C++ coverage will not work.)
endif
ifndef OTIO_CXX_BUILD_TMP_DIR
	$(error $(newline)Error: unless compiled with OTIO_CXX_BUILD_TMP_DIR, \
		C++ coverage will not work, because intermediate build products will \
		not be found.)
endif
	lcov --capture -b . --directory ${OTIO_CXX_BUILD_TMP_DIR} \
		--output-file=${OTIO_CXX_BUILD_TMP_DIR}/coverage.info -q
	cat ${OTIO_CXX_BUILD_TMP_DIR}/coverage.info | sed "s/SF:.*src/SF:src/g"\
		> ${OTIO_CXX_BUILD_TMP_DIR}/coverage.filtered.info
	lcov --remove ${OTIO_CXX_BUILD_TMP_DIR}/coverage.filtered.info '/usr/*' \
		--output-file=${OTIO_CXX_BUILD_TMP_DIR}/coverage.filtered.info -q
	lcov --remove ${OTIO_CXX_BUILD_TMP_DIR}/coverage.filtered.info '*/deps/*' \
		--output-file=${OTIO_CXX_BUILD_TMP_DIR}/coverage.filtered.info -q
	rm ${OTIO_CXX_BUILD_TMP_DIR}/coverage.info
	lcov --list ${OTIO_CXX_BUILD_TMP_DIR}/coverage.filtered.info

# run all the unit tests, stopping at the first failure
test_first_fail: python-version
	@python -m unittest discover -s tests --failfast

clean:
ifdef COV_PROG
	@${COV_PROG} erase
endif
	@${MAKE_PROG} -C contrib/opentimelineio_contrib/adapters clean VERBOSE=$(VERBOSE)
	rm -vf *.whl
	@cd docs; ${MAKE_PROG} clean

# conform all files to pep8 -- WILL CHANGE FILES IN PLACE
# autopep8:
# ifndef AUTOPEP8_PROG
# 	$(error "autopep8 is not available please see: "\
# 		"https://pypi.python.org/pypi/autopep8#installation")
# endif
# 	find . -name "*.py" | xargs ${AUTOPEP8_PROG} --aggressive --in-place -r

# run the codebase through flake8.  pep8 and pyflakes are called by flake8.
lint:
ifndef PYCODESTYLE_PROG
	$(error $(newline)$(ccred)pycodestyle is not available on $$PATH please see:$(newline)$(ccend)\
	$(ccblue)	https://pypi.python.org/pypi/pep8#installation$(newline)$(ccend)\
	$(dev_deps_message))
endif
ifndef PYFLAKES_PROG
	$(error $(newline)$(ccred)pyflakes is not available on $$PATH please see:$(newline)$(ccend)\
	$(ccblue)	https://pypi.python.org/pypi/pyflakes#installation$(newline)$(ccend)\
	$(dev_deps_message))
endif
ifndef FLAKE8_PROG
	$(error $(newline)$(ccred)flake8 is not available on $$PATH please see:$(newline)$(ccend)\
	$(ccblue)	http://flake8.pycqa.org/en/latest/index.html#installation$(newline)$(ccend)\
	$(dev_deps_message))
endif
	@python -m flake8

# build python wheel package for the available python version
wheel:
	@pip wheel . --no-deps

# format all .h and .cpp files using clang-format
format:
ifndef CLANG_FORMAT_PROG
	$(error $(newline)$(ccred)clang-format is not available on $$PATH$(ccend))
endif
	$(eval DIRS = src/opentime src/opentimelineio)
	$(eval DIRS += src/py-opentimelineio/opentime-opentime-bindings) 
	$(eval DIRS += src/py-opentimelineio/opentimelineio-opentime-bindings)
	$(eval FILES_TO_FORMAT = $(wildcard $(addsuffix /*.h, $(DIRS)) $(addsuffix /*.cpp, $(DIRS))))
	$(shell clang-format -i -style=file $(FILES_TO_FORMAT))

manifest:
ifndef CHECK_MANIFEST_PROG
	$(error $(newline)$(ccred)check-manifest is not available on $$PATH please see:$(newline)$(ccend)\
	$(ccblue)	https://github.com/mgedmin/check-manifest#quick-start$(newline)$(ccend)\
	$(dev_deps_message))
endif
	@check-manifest
	@echo "check-manifest succeeded"
	

doc-model:
	@python src/py-opentimelineio/opentimelineio/console/autogen_serialized_datamodel.py --dryrun

doc-model-update:
	@python src/py-opentimelineio/opentimelineio/console/autogen_serialized_datamodel.py -o docs/tutorials/otio-serialized-schema.md

doc-plugins:
	@python src/py-opentimelineio/opentimelineio/console/autogen_plugin_documentation.py --dryrun

doc-plugins-update:
	@python src/py-opentimelineio/opentimelineio/console/autogen_plugin_documentation.py -o docs/tutorials/otio-plugins.md --public-only --sanitized-paths

# build the CORE_VERSION_MAP cpp file
version-map:
	@python src/py-opentimelineio/opentimelineio/console/autogen_version_map.py -i src/opentimelineio/CORE_VERSION_MAP.last.cpp --dryrun

version-map-update:
	@echo "updating the CORE_VERSION_MAP..."
	@python src/py-opentimelineio/opentimelineio/console/autogen_version_map.py -i src/opentimelineio/CORE_VERSION_MAP.last.cpp -o src/opentimelineio/CORE_VERSION_MAP.cpp

# generate documentation in html
doc-html:
	@# if you just want to build the docs yourself outside of RTD
	@cd docs; ${MAKE_PROG} html

doc-cpp: 
	@cd doxygen ; doxygen config/dox_config ; cd .. 
	@echo "wrote doxygen output to: doxygen/output/html/index.html"
	
# release related targets
confirm-release-intent:
ifndef OTIO_DO_RELEASE
	$(error \
		"If you are sure you want to perform a release, set OTIO_DO_RELEASE=1")
endif
	@echo "Starting release process..."

check-git-status:
ifneq ($(GITSTATUS), 0)
	$(error \
		"Git repository is dirty, cannot create release. Run 'git status' \
		for more info")
endif
	@echo "Git status is clean, ready to proceed with release."

verify-license:
	@echo "Verifying licenses in files..."
	@python maintainers/verify_license.py -s .

fix-license:
	@python maintainers/verify_license.py -s . -f

freeze-ci-versions:
	@echo "freezing CI versions..."
	@python maintainers/freeze_ci_versions.py -f

unfreeze-ci-versions:
	@echo "unfreezing CI versions..."
	@python maintainers/freeze_ci_versions.py -u

# needs to happen _before_ version-map-update so that version in 
# CORE_VERSION_MAP does not have the .dev1 suffix at release time
remove-dev-suffix:
	@echo "Removing .dev1 suffix"
	@python maintainers/remove_dev_suffix.py -r

check-github-token:
ifndef OTIO_RELEASE_GITHUB_TOKEN
	$(error \
		OTIO_RELEASE_GITHUB_TOKEN is not set, unable to update contributors)
endif

update-contributors: check-github-token
	@echo "Updating CONTRIBUTORS.md..."
	@python maintainers/fetch_contributors.py \
		--repo AcademySoftwareFoundation/OpenTimelineIO \
		--token $(OTIO_RELEASE_GITHUB_TOKEN)

dev-python-install:
	@python setup.py install

# make target for preparing a release candidate 
release: \
	confirm-release-intent \
	check-git-status \
	check-github-token \
	verify-license \
	freeze-ci-versions \
	remove-dev-suffix \
	format \
	dev-python-install \
	version-map-update \
	test-core \
	update-contributors 
	@echo "Release is ready.  Commit, push and open a PR!"

# targets for creating a new version (after making a release, to start the next
# development cycle)
bump-otio-minor-version:
	@python maintainers/bump_version_number.py -i minor

shuffle-core-version-map:
	@cp -f src/opentimelineio/CORE_VERSION_MAP.cpp \
		src/opentimelineio/CORE_VERSION_MAP.last.cpp
	@echo "set the current version map as the next one"

add-dev-suffix:
	@echo "Adding .dev1 suffix"
	@python maintainers/remove_dev_suffix.py -a

# make target for starting a new version (after a release is completed)
start-dev-new-minor-version: \
	check-git-status \
	unfreeze-ci-versions \
	bump-otio-minor-version \
	shuffle-core-version-map \
	add-dev-suffix \
	dev-python-install \
	version-map-update \
	test-core
	@echo "New version made.  Commit, push and open a PR!"
