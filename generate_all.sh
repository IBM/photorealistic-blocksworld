#!/bin/bash -x


# blender -noaudio \
#         --background --python render_all_images.py -- \
#         --render-num-samples 200 \
#         --output-dir output-5-3 \
#         --width 150 \
#         --height 100 \
#         --num-objects 5 \
#         --max-stacks 3 \
#         --use-gpu 1 --dry-run
# 
# 80639 states
# 518399 transitions

blender -noaudio \
        --background --python render_all_images.py -- \
        --render-num-samples 200 \
        --output-dir output-5-3-single \
        --width 150 \
        --height 100 \
        --num-objects 5 \
        --max-stacks 3 \
        --use-gpu 1 --dry-run
