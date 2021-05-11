#!/bin/bash

dir=$(readlink -ef $(dirname $0))

export proj=$(date +%Y%m%d%H%M)-render-problems
SUBMIT=${SUBMIT:-"jbsub -mem 4g -cores 1+1 -queue x86_1h -proj $proj -require k80"}

# 1,2,3 are for debugging ; 7 and 14 are for final experiments
parallel --line-buffer $SUBMIT $dir/generate_problems.sh ::: {3..6} ::: 007 014
