#!/bin/bash


jbsub -queue x86_1h \
      blender -noaudio \
      --background --python render_all_images.py -- \
      --render-num-samples 200 \
      --initial-objects init-4-4.json \
      --width 150 \
      --height 100 \
      --num-objects 4 \
      --max-stacks 4 \
      --dry-run
