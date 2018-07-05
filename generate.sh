#!/bin/bash -x

blender -noaudio \
        --background --python render_images.py -- \
        --num-images 10000 \
        --render-num-samples 200 \
        --width 300 \
        --height 200 \
        --num-objects 7 \
        --max-stacks 4 \
        --use-gpu 1

parallel ./extract_region.py ::: output/scenes/*.json

