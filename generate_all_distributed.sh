#!/bin/bash -x

# 80639 states
# 518399 transitions
# 404 jobs

NPROC=$1

blender -noaudio \
        --background --python render_all_images.py -- \
        --render-num-samples 200 \
        --initial-objects init-5-3.json \
        --output-dir output-5-3-distributed \
        --start-idx $((($NPROC-1)*200)) \
        --num-images 200 \
        --width 150 \
        --height 100 \
        --num-objects 5 \
        --max-stacks 3 \
        --use-gpu 1



