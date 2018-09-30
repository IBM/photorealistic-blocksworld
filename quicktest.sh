#!/bin/bash -x

blender -noaudio \
        --background --python render_images.py -- \
        --num-images 1 \
        --render-num-samples 10 \
        --width 600 \
        --height 400 \
        --num-objects 10 \
        --max-stacks 5


./extract_region.py output/scenes/CLEVR_new_000000_pre.json
./extract_region.py output/scenes/CLEVR_new_000000_suc.json

./extract_regions_binary.py output
