#!/bin/bash

d0=$(pwd)
d=$(dirname "$0")

cd "$d"

docker run \
    --rm \
    -v $(pwd):/tmp/install/requirements \
    --workdir /tmp/install \
    python:3.8 \
    sh -c "\
        pip install -r requirements/00-base.txt && \
        pip freeze > requirements/00-base-locked.txt && \
        echo '' && \
        cat requirements/00-base-locked.txt && \
        echo '-----' && \
        pip install -r requirements/00-base-locked.txt -r requirements/10-dev.txt && \
        pip freeze > requirements/10-dev-locked.txt && \
        echo '' && \
        cat requirements/10-dev-locked.txt && \
        echo ''
        "

cd "$d0"
