#!/usr/bin/env bash

set -e

cslc ./layout.csl --fabric-dims=13,13 \
--fabric-offsets=4,1 --params=WIDTH:3,HEIGHT:3 -o out --memcpy --channels 1
cs_python run.py --name out