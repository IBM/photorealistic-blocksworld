#!/bin/bash -x

blender -noaudio \
        --background --python render_images.py -- \
        --num-images 1 \
        --render-num-samples 200 \
        --width 1920 \
        --height 1080 \
        --num-objects 7 \
        --max-stacks 4 \
        --use-gpu 1

./extract_region.py output/scenes/CLEVR_new_000000_pre.json
./extract_region.py output/scenes/CLEVR_new_000000_suc.json
