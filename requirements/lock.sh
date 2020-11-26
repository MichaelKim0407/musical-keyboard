#!/bin/bash

d0=$(pwd)
d=$(dirname "$0")

cd "$d"

docker run \
    --rm \
    -v $(pwd):/tmp/install \
    --workdir /tmp/install \
    python:3.8 \
    sh -c "\
        pip install -r 00-base.txt && \
        pip freeze > 00-base-locked.txt && \
        cat 00-base-locked.txt \
        "

cd "$d0"
