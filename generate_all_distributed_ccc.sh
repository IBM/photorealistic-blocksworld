#!/bin/bash


common="-mem 4g -queue x86_1h -proj $(date -Iminutes)"
# dir=$(dirname $(dirname $(readlink -ef $0)))
# export PYTHONPATH=$dir:$PYTHONPATH
# export PYTHONUNBUFFERED=1

parallel "$common ./generate_all_distributed.sh {}" ::: $(seq 100)

