#!/bin/bash -x

blender --background --python render_images.py -- \
        --num-images 10 \
        --render-num-samples 40 \
        --width 300 \
        --height 200 \
        --num-objects 10 \
        --max-stacks 6

