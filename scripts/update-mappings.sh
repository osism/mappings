#!/usr/bin/env bash

buildah build-using-dockerfile \
    --format docker \
    --tag mappings \
    . >&2

# stdout of the generator is the summary of changes that the
# update-mappings workflow uses as the PR body
podman run --rm -v $(pwd):/output mappings
