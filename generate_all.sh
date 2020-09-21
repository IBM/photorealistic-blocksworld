#!/bin/bash -x

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

objs=${1:-2}
num_images=${2:-200}
distributed=${3:-false}
num_jobs=${4:-1}
gpu=${5:-true}
suffix=$6

prefix="blocks-$objs$suffix"
proj=$(date +%Y%m%d%H%M)-render-$prefix
use_gpu=""
if $gpu
then
    use_gpu="--use-gpu 1"
fi
  

submit="jbsub -mem 4g -cores 1+1 -queue x86_1h -proj $proj"

blenderdir=$(echo blender-2.*/)
blender="$blenderdir/blender -noaudio --background --python render_images.py -- \
      --output-dir      $prefix                   \
      --render-num-samples 300                           \
      --width 300                                        \
      --height 200                                       \
      --num-objects $objs                               "

if $distributed
then
    num_images_per_job=$((num_images/num_jobs))
    parallel "$submit $blender $use_gpu --start-idx {} --num-images $num_images_per_job" ::: $(seq 0 $num_images_per_job $num_images)
    echo "Run the following command when all jobs have finished:"
    echo "./extract_all_regions_binary.py --out $prefix.npz $prefix/"
else
    $blender $use_gpu --num-images $num_images
    ./extract_all_regions_binary.py --out $prefix.npz $prefix/
fi
