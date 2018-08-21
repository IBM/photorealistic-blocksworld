#!/bin/bash -x

blender -noaudio \
        --background --python render_all_images.py -- \
        --render-num-samples 200 \
        --output-scene-dir output/scenes/ \
        --output-image-dir output/images/ \
        --output-scene-file output/scene.json \
        --width 300 \
        --height 200 \
        --num-objects 3 \
        --max-stacks 4

# parallel ./extract_region.py ::: output/scenes/*.json

