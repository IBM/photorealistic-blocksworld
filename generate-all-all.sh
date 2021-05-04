#!/bin/bash

set -e

parallel ./generate_all.sh {} 40000 50 ::: {3..6}

echo render-cylinders-{3..6}
watch-proj render-cylinders-{3..6}

parallel --line-buffer -v ./merge-npz.py --out cylinders-{1}-{2}.npz cylinders-{1}/*-{2}.npz ::: {3..6} ::: objs bgnd flat high
