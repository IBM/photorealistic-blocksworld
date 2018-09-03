#!/bin/bash -x

objs=${1:-2}
stacks=${2:-2}
distributed=${3:-false}
num_images=${4:-200}
prefix="blocks-$objs-$stacks"
proj=$(date +%Y%m%d%H%M)-render-$prefix
jbsub="jbsub -mem 4g -cores 1+1 -queue x86_1h -proj $proj"

blender="blender -noaudio --background --python render_all_images.py -- \
      --output-dir      $prefix                   \
      --initial-objects $prefix-init.json                \
      --statistics      $prefix-stat.json                \
      --render-num-samples 300                           \
      --width 300                                        \
      --height 200                                       \
      --num-objects $objs                                \
      --max-stacks $stacks                               "

$blender --dry-run              # necessary for init-o-s.json

states=$(jq      .states      $prefix-stat.json)
transitions=$(jq .transitions $prefix-stat.json)

if $distributed
then
    parallel "$jbsub $blender --use-gpu 1 --start-idx {} --num-images $num_images" ::: $(seq 0 $num_images $states)
    ccc/watch-proj $proj && $jbsub "./extract_all_regions_binary.py --out $prefix.npz $prefix/"
else
    $jbsub "$blender --use-gpu 1 ; ./extract_all_regions_binary.py --out $prefix.npz $prefix/"
fi
