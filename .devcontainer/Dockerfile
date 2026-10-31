# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

FROM ghcr.io/astral-sh/uv:0.13.6 AS uv
FROM aswf/ci-otio:2026

USER root
COPY --from=uv /uv /uvx /usr/local/bin/
RUN useradd --user-group --create-home --shell /bin/bash vscode

ENV HOME=/home/vscode \
    UV_CACHE_DIR=/home/vscode/.cache/uv \
    UV_PROJECT_ENVIRONMENT=/home/vscode/.venv \
    UV_NO_MANAGED_PYTHON=1 \
    UV_PYTHON_DOWNLOADS=never \
    SKBUILD_BUILD_DIR=/home/vscode/.cache/otio/build/{wheel_tag} \
    CC=gcc \
    CXX=g++

# Match the VFX CI build: use the image's libraries, never fetch submodules.
ENV CMAKE_ARGS="-DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DCMAKE_CXX_STANDARD=20 -DOTIO_AUTOMATIC_SUBMODULES=OFF -DOTIO_CXX_EXAMPLES=OFF -DOTIO_DEPENDENCIES_INSTALL=OFF -DOTIO_FIND_IMATH=ON -DOTIO_FIND_PYBIND11=ON -DOTIO_FIND_RAPIDJSON=ON -DOTIO_FIND_MINIZIP_NG=ON"

USER vscode
