#!/bin/bash -x

blender -noaudio \
        --background --python render_all_images.py -- \
        --render-num-samples 200 \
        --output-scene-dir output11/scenes/ \
        --output-image-dir output11/images/ \
        --output-scene-file output11/scene.json \
        --width 300 \
        --height 200 \
        --num-objects 1 \
        --max-stacks 1 \
        --use-gpu 1


blender -noaudio \
        --background --python render_all_images.py -- \
        --render-num-samples 200 \
        --output-scene-dir output12/scenes/ \
        --output-image-dir output12/images/ \
        --output-scene-file output12/scene.json \
        --width 300 \
        --height 200 \
        --num-objects 1 \
        --max-stacks 2 \
        --use-gpu 1

