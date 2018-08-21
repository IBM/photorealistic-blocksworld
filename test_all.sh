#!/bin/bash -x

blender -noaudio \
        --background --python render_images.py -- \
        --render-num-samples 200 \
        --width 1920 \
        --height 1080 \
        --num-objects 4 \
        --max-stacks 3


