#!/bin/bash -x

blender -noaudio \
        --background --python render_images.py -- \
        --num-images 20000 \
        --render-num-samples 200 \
        --width 600 \
        --height 400 \
        --num-objects 10 \
        --max-stacks 5 \
        --use-gpu 1

parallel ./extract_region.py ::: output/scenes/*.json

