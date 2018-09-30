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

objs=${1:-2}
stacks=${2:-2}
distributed=${3:-false}
num_images=${4:-200}
prefix="blocks-$objs-$stacks"
proj=$(date +%Y%m%d%H%M)-render-$prefix

submit="jbsub -mem 4g -cores 1+1 -queue x86_1h -proj $proj"

blender="blender -noaudio --background --python render_images.py -- \
      --output-dir      $prefix                   \
      --initial-objects $prefix-init.json                \
      --statistics      $prefix-stat.json                \
      --render-num-samples 300                           \
      --width 300                                        \
      --height 200                                       \
      --num-objects $objs                                \
      --max-stacks $stacks                               "

$blender --dry-run || exit 1      # necessary for init-o-s.json

states=$(jq      .states      $prefix-stat.json)
transitions=$(jq .transitions $prefix-stat.json)

if $distributed
then
    parallel "$submit $blender --use-gpu 1 --start-idx {} --num-images $num_images" ::: $(seq 0 $num_images $states)
    echo "Run the following command when all jobs have finished:"
    echo "./extract_all_regions_binary.py --out $prefix.npz $prefix/"
else
    $blender --use-gpu 1
    ./extract_all_regions_binary.py --out $prefix.npz $prefix/
fi
