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


# 100 jobs

NPROC=$1

blender -noaudio \
        --background --python render_all_images.py -- \
        --render-num-samples 200 \
        --initial-objects init-4-4.json \
        --output-dir output-4-4 \
        --start-idx $((($NPROC-1)*200)) \
        --num-images 200 \
        --width 150 \
        --height 100 \
        --num-objects 4 \
        --max-stacks 4 \
        --use-gpu 1



