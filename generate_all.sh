#!/bin/bash -x

# Render all scenes with a given number of objects and stacks.
#
# generate_all.sh [objs] [stacks] [distributed] [num_images]
#
#   objs:   specity the number of objects, default = 2
# 
#   stacks: specity the number of stacks,  default = 2
# 
#   distributed: Whether to split the jobs and run the rendering in parallel. true|false. default = false
# 
#   num_images:  The number of images per job when distributed=true.
#
# You can modity the "submit" variable in the source code to
# customize the job submission commands for the job scheduler in your cluster.

min=${1:-3}
max=${2:-8}
distributed=${3:-false}
num_images=${4:-200}
gpu=${5:true}
prefix="clevr-$min-$max"
proj=$(date +%Y%m%d%H%M)-render-$prefix

if $gpu
then
    gpuflag="--use-gpu 1"
else
    gpuflag=""
fi

submit="jbsub -mem 4g -cores 1+1 -queue x86_1h -proj $proj"

blender="blender -noaudio --background --python render_images.py -- \
      --output-dir      $prefix                   \
      --width 300                                 \
      --height 200                                \
      --min-objects $min                          \
      --max-objects $max                          "

if $distributed
then
    parallel "$submit $blender $gpuflag --start-idx {} --num-images $num_images --render-num-samples 300" ::: $(seq 0 $num_images $states)
    echo "Run the following command when all jobs have finished:"
    echo "./extract_all_regions_binary.py --out $prefix.npz $prefix/"
else
    $blender $gpuflag --num-images $num_images --render-num-samples 40
    ./extract_all_regions_binary.py --out $prefix.npz $prefix/
fi


# example:
# single pc:   ./generate_all.sh 3 6 false 10 false
# distributed: ./generate_all.sh 3 6 true 10 true
# distributed: ./generate_all.sh 3 6 true

