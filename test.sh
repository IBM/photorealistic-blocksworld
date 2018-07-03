#!/bin/bash -x


blender --background --python render_images.py -- --num-images 1 --render-num-samples 5 --width 800 --height 600
