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

export objs=${1:-3} ; shift 1
export steps=${1:-4} ; shift 1
export num_problems=${1:-20} ; shift 1
export num_samples_per_state=${1:-10} ; shift 1
export gpu=${1:-true} ; shift 1
export suffix=$1 ; shift 1

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
    $blenderdir/blender -noaudio --background --python render_images.py -- \
                        --properties-json data/cylinders-properties.json \
                        --render-num-samples 150 \
                        --width 150              \
                        --height 100             \
                        --num-objects $objs      \
                        --num-steps $steps       \
                        $use_gpu                 \
                        --output-dir $output_dir \
                        --randomize-colors       \
                        --key-light-jitter 1.0   \
                        --fill-light-jitter 1.0  \
                        --back-light-jitter 1.0  \
                        --camera-jitter 0.5      \
                        --object-jitter 0.1      \
                        --num-transitions 1 \
                        --num-samples-per-state $num_samples_per_state
    ./extract_all_regions_binary.py --num-samples-per-state $num_samples_per_state --as-problem --out $output_dir/objs.npz --resize 16 16 $output_dir
    ./extract_all_regions_binary.py --num-samples-per-state $num_samples_per_state --as-problem --out $output_dir/bgnd.npz --resize 16 16 --include-background $output_dir
    ./extract_all_regions_binary.py --num-samples-per-state $num_samples_per_state --as-problem --out $output_dir/flat.npz --resize 30 45 --include-background --exclude-objects $output_dir
    ./extract_all_regions_binary.py --num-samples-per-state $num_samples_per_state --as-problem --out $output_dir/high.npz --resize 80 120 --include-background --exclude-objects $output_dir
}

for i in $(seq $num_problems)
do
    job $dir/$steps-$(printf "%03d" $i)
done

