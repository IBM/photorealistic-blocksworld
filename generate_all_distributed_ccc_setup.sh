#!/bin/bash


jbsub -queue x86_1h \
      blender -noaudio \
      --background --python render_all_images.py -- \
      --render-num-samples 200 \
      --output-dir output-5-3-distributed \
      --initial-objects init-5-3.json \
      --width 150 \
      --height 100 \
      --num-objects 5 \
      --max-stacks 3 \
      --dry-run
