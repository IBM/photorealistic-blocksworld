#!/bin/bash

set -e

dir=$(readlink -ef $(dirname $0))

parallel $dir/generate_all.sh {} 40000 3 50 ::: {3..7}

echo render-cylinders-{3..7}
watch-proj render-cylinders-{3..7}

parallel --line-buffer -v $dir/merge-npz.py --out cylinders-{1}-{2}.npz cylinders-{1}/*-{2}.npz ::: {3..7} ::: objs bgnd flat high
