#!/usr/bin/env bash

docker build \
    --tag mappings \
    .

docker run --rm -v $(pwd):/output mappings
