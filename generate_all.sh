#!/bin/bash

# Render all scenes with a given number of objects and stacks.
#
# generate_all.sh [objs] [stacks] [distributed] [num_images] [gpu]
#
#   objs:   specity the number of objects, default = 2
# 
#   num_images:  The number of images to be rendered in total.
#
#   distributed: Whether to split the jobs and run the rendering in parallel. true|false. default = false
# 
#   num_jobs: how many jobs to use when distributed.
# 
#   gpu:  if true, use the gpu. default : true.

#
# You can modity the "submit" variable in the source code to
# customize the job submission commands for the job scheduler in your cluster.

export objs=${1:-2}
export num_images=${2:-200}
export distributed=${3:-false}
export num_jobs=${4:-1}
export gpu=${5:-true}
export suffix=$6

export dir="blocks-$objs$suffix"
export proj=$(date +%Y%m%d%H%M)-render-$dir
export use_gpu=""
if $gpu
then
    export use_gpu="--use-gpu 1"
fi
  

submit="jbsub -mem 4g -cores 1+1 -queue x86_1h -proj $proj"

job (){
    output_dir=$1
    start_idx=$2
    num_images=$3
    blenderdir=$(echo blender-2.*/)
    $blenderdir/blender -noaudio --background --python render_images.py -- \
                        --render-num-samples 300 \
                        --width 300              \
                        --height 200             \
                        --num-objects $objs      \
                        $use_gpu                 \
                        --output-dir $output_dir \
                        --start-idx $start_idx   \
                        --num-images $num_images
    ./extract_all_regions_binary.py --out $output_dir.npz $output_dir
}

export -f job
# for parallel to recognize the shell function
export SHELL=/bin/bash

if $distributed
then
    num_images_per_job=$((num_images/num_jobs))
    parallel "$submit job $dir/{} {} $num_images_per_job" ::: $(seq 0 $num_images_per_job $((num_images-num_images_per_job)))
    echo "Run the following command when all jobs have finished:"
    echo "./merge-npz.py --out $dir.npz $dir/*.npz"
else
    job $dir 0 $num_images
fi
