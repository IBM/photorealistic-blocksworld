#!/bin/bash -x

# blender -noaudio \
#         --background --python render_all_images.py -- \
#         --render-num-samples 200 \
#         --output-dir output-2-2 \
#         --width 150 \
#         --height 100 \
#         --num-objects 2 \
#         --max-stacks 2 \
#         --use-gpu 1 --dry-run
# 
# 98302 states
# 1075200 transitions


# 100 jobs

NPROC=$1

blender -noaudio \
        --background --python render_all_images.py -- \
        --render-num-samples 200 \
        --initial-objects init-2-2.json \
        --output-dir output-2-2-distributed \
        --start-idx $((($NPROC-1)*8)) \
        --num-images 8 \
        --width 150 \
        --height 100 \
        --num-objects 2 \
        --max-stacks 2 \
        --use-gpu 1



