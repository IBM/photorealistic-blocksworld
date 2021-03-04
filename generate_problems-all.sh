#!/bin/bash

export proj=$(date +%Y%m%d%H%M)-render-problems
SUBMIT=${SUBMIT:-"jbsub -mem 4g -cores 1+1 -queue x86_1h -proj $proj -require k80"}

parallel --line-buffer $SUBMIT ./generate_problems.sh ::: 3 4 5 6 ::: 1 2 3 5 8 13 21
