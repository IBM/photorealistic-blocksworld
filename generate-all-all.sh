#!/bin/bash

set -e

parallel ./generate_all.sh {} 40000 50 ::: {3..6}

echo render-monoblocks-{3..6}
watch-proj render-monoblocks-{3..6}

parallel --line-buffer -v ./merge-npz.py --out monoblocks-{1}-{2}.npz monoblocks-{1}/*-{2}.npz ::: {3..6} ::: objs bgnd flat high
