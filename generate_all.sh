#!/bin/bash -x

blender -noaudio \
        --background --python render_all_images.py -- \
        --render-num-samples 200 \
        --output-dir output-4-4 \
        --width 150 \
        --height 100 \
        --num-objects 4 \
        --max-stacks 4 \
        --use-gpu 1

# parallel ./extract_region.py ::: output/scenes/*.json

