#!/bin/bash

set -e

dir=$(readlink -ef $(dirname $0))

parallel $dir/generate-dataset.sh {} 40000 1 50 ::: {3..7}

echo render-cylinders-{3..7}
watch-proj render-cylinders-{3..7}

parallel -j 8 --line-buffer -v $dir/merge-npz.py --out cylinders-{1}-{2}.npz cylinders-{1}/*-{2}.npz ::: {3..7} ::: objs bgnd flat high
