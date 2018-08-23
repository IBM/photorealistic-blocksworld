#!/bin/bash


common="jbsub -mem 4g -cores 1+1 -queue x86_1h -proj $(date -Iminutes)"
# dir=$(dirname $(dirname $(readlink -ef $0)))
# export PYTHONPATH=$dir:$PYTHONPATH
# export PYTHONUNBUFFERED=1

parallel "$common ./generate_all_distributed.sh {}" ::: $(seq 404)

