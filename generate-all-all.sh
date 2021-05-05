#!/bin/bash

set -e

dir=$(readlink -ef $(dirname $0))

parallel $dir/generate_all.sh {} 40000 50 ::: {3..6}

echo render-cylinders-{3..6}
watch-proj render-cylinders-{3..6}

parallel --line-buffer -v $dir/merge-npz.py --out cylinders-{1}-{2}.npz cylinders-{1}/*-{2}.npz ::: {3..6} ::: objs bgnd flat high
