#!/bin/bash

if [ -z "$@" ]
then

    cat <<EOF >&2


    Usage: generate_problems.sh [objs] [steps] [num_problems] [gpu] [suffix]

      objs:   specity the number of objects, default = 2

      steps:   specity the number of random actions to perform, default = 4

      num_problems:  The number of problems to be rendered in total.

      gpu:  if true, use the gpu. default : true.

      suffix:  arbitrary string to be attached to the name of the output directory.


    Render a pair of scenes, where the second one is a shuffled state.
    The pair can be seen as an initial and the goal configuration of a planning task.
    It also runs extract_all_regions_binary.

    Use it like this: ./generate_problems.sh 5 5 1

EOF
    exit 1
fi

export objs=${1:-3}
export steps=${2:-4}
export num_problems=${3:-30}
export gpu=${4:-true}
export suffix=$5

export dir="prob-cylinders-$objs$suffix"
export proj=$(date +%Y%m%d%H%M)-render-$dir
export use_gpu=""
if $gpu
then
    export use_gpu="--use-gpu 1"
fi

job (){
    output_dir=$1
    blenderdir=$(ls -d blender-2.*/ | tail -n 1)
    $blenderdir/blender -noaudio --background --python render_problem.py -- \
                        --properties-json data/cylinders-properties.json \
                        --allow-duplicates \
                        --render-num-samples 150 \
                        --width 150              \
                        --height 100             \
                        --num-objects $objs      \
                        --num-steps $steps      \
                        $use_gpu                 \
                        --output-dir $output_dir
    ./extract_all_regions_binary.py --as-problem --out $output_dir/objs.npz --resize 16 16 $output_dir
    ./extract_all_regions_binary.py --as-problem --out $output_dir/bgnd.npz --resize 16 16 --include-background $output_dir
    ./extract_all_regions_binary.py --as-problem --out $output_dir/flat.npz --resize 30 45 --include-background --exclude-objects $output_dir
    ./extract_all_regions_binary.py --as-problem --out $output_dir/high.npz --resize 80 120 --include-background --exclude-objects $output_dir
    ./extract_all_regions_binary.py --resize-image --resize 30 45 $output_dir
}

for i in $(seq $num_problems)
do
    job $dir/$steps-$i
done

