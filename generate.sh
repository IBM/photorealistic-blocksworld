#!/bin/bash -x

blender -noaudio \
        --background --python render_images.py -- \
        --num-images 20000 \
        --render-num-samples 100 \
        --width 300 \
        --height 200 \
        --num-objects 10 \
        --max-stacks 5 \
        --use_gpu 1

parallel ./extract_region.py ::: output/scenes/*.json

