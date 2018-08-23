#!/bin/bash -x


# blender -noaudio \
#         --background --python render_all_images.py -- \
#         --render-num-samples 200 \
#         --output-dir output-4-4 \
#         --width 150 \
#         --height 100 \
#         --num-objects 4 \
#         --max-stacks 4 \
#         --use-gpu 1 --dry-run
# 
# 98304 states
# 1075200 transitions

blender -noaudio \
        --background --python render_all_images.py -- \
        --render-num-samples 200 \
        --output-dir output-4-4-single \
        --width 150 \
        --height 100 \
        --num-objects 4 \
        --max-stacks 4 \
        --use-gpu 1
