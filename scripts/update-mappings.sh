#!/usr/bin/env bash

buildah build-using-dockerfile \
    --format docker \
    --tag mappings \
    .

podman run --rm -v $(pwd):/output mappings
