#!/bin/bash

blender --background -noaudio --python render_images.py -- \
        --num-images 10 \
        --width 300 \
        --height 200 \
        --render-num-samples 20 \
        --max-objects 4

./extract_region.py output/scene/CLEVR_new_000000.json
