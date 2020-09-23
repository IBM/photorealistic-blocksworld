#!/bin/bash

# Render a pair of scenes, where the second one is a shuffled state.
# It also runs extract_all_regions_binary.

# The pair can be seen as an initial and the goal configuration of a planning task.

# generate-blocks-problem.sh [objs] [num_problems] [gpu]
#
#   objs:   specity the number of objects, default = 2
# 
#   num_problems:  The number of problems to be rendered in total.
#
#   gpu:  if true, use the gpu. default : true.

export objs=${1:-3}
export num_problems=${2:-30}
export gpu=${3:-true}
export suffix=$4

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
                        $use_gpu                 \
                        --output-dir $output_dir
    ./extract_all_regions_binary.py --out $output_dir/problem.npz $output_dir
}

for i in $(seq $num_problems)
do
    job $dir/$i
done

