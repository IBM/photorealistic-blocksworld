#!/bin/bash -x

objs=${1:-2}
stacks=${2:-2}
distributed=${3:-false}
proj=$(date +%Y%m%d%H%M)
jbsub="jbsub -mem 4g -cores 1+1 -queue x86_1h -proj $proj"


blender="blender -noaudio --background --python render_all_images.py --
      --output-dir output-$objs-$stacks
      --render-num-samples 300
      --initial-objects init-$objs-$stacks.json
      --statistics      stat-$objs-$stacks.json
      --width 300
      --height 200
      --num-objects $objs
      --max-stacks $stacks
      --use-gpu 1"

$blender --dry-run              # necessary for init-o-s.json

states=$(jq      .states      stat-$objs-$stacks.json)
transitions=$(jq .transitions stat-$objs-$stacks.json)

if $distributed
then
    parallel "$jbsub $blender --start-idx {} --num-images 8 --use-gpu 1" ::: $(seq 0 200 $states)
    ccc/watch-proj $proj && $jbsub "./extract_all_regions_binary.py --out blocksworld-$objs-$stacks.npz output-$objs-$stacks/"
else
    $jbsub "$blender ; ./extract_all_regions_binary.py --out blocksworld-$objs-$stacks.npz output-$objs-$stacks/"
fi
