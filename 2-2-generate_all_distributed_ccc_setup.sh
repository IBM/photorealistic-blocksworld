#!/bin/bash


jbsub -queue x86_1h \
      blender -noaudio \
      --background --python render_all_images.py -- \
      --output-dir output-2-2-distributed \
      --render-num-samples 200 \
      --initial-objects init-2-2.json \
      --width 150 \
      --height 100 \
      --num-objects 2 \
      --max-stacks 2 \
      --dry-run
