#!/bin/bash -x

blender --background --python render_images.py -- \
        --num-images 10 \
        --render-num-samples 40 \
        --width 300 \
        --height 200 \
        --num-objects 10 \
        --max-stacks 6


./extract_region.py output/scenes/CLEVR_new_000000_pre.json
./extract_region.py output/scenes/CLEVR_new_000000_suc.json
