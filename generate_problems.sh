#!/bin/bash

# Render a pair of scenes, where the second one is a shuffled state.
# It also runs extract_all_regions_binary.

# The pair can be seen as an initial and the goal configuration of a planning task.

# generate_problems.sh [objs] [steps] [num_problems] [gpu] [suffix]
#
#   objs:   specity the number of objects, default = 2
#
#   steps:   specity the number of random actions to perform, default = 4
# 
#   num_problems:  The number of problems to be rendered in total.
#
#   gpu:  if true, use the gpu. default : true.
#
#   suffix:  arbitrary string to be attached to the name of the output directory.
# 
#
# use it like: parallel --line-buffer ./generate_problems.sh {} 10 ::: 3 4 5 6 ::: 1 2 3 5 8 13 21

export objs=${1:-3}
export steps=${2:-4}
export num_problems=${3:-30}
export gpu=${4:-true}
export suffix=$5

export dir="prob-blocks-$objs$suffix"
export proj=$(date +%Y%m%d%H%M)-render-$dir
export use_gpu=""
if $gpu
then
    export use_gpu="--use-gpu 1"
fi

job (){
    output_dir=$1
    blenderdir=$(echo blender-2.*/)
    $blenderdir/blender -noaudio --background --python render_problem.py -- \
                        --render-num-samples 300 \
                        --width 300              \
                        --height 200             \
                        --num-objects $objs      \
                        --num-steps $steps      \
                        $use_gpu                 \
                        --output-dir $output_dir
    ./extract_all_regions_binary.py --as-problem --out $output_dir/problem.npz $output_dir
}

for i in $(seq $num_problems)
do
    job $dir/$steps-$i
done

