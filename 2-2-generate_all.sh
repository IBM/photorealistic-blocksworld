#!/bin/bash -x


# blender -noaudio \
#         --background --python render_all_images.py -- \
#         --render-num-samples 200 \
#         --output-dir output-4-4 \
#         --width 150 \
#         --height 100 \
#         --num-objects 4 \
#         --max-stacks 4 \
#         --use-gpu 1 --dry-run
# 
# 98304 states
# 1075200 transitions

jbsub -mem 4g -cores 1+1 -queue x86_1h -proj $(date -Iminutes) \
      blender -noaudio \
        --background --python render_all_images.py -- \
        --render-num-samples 200 \
        --output-dir output-2-2-single \
        --width 150 \
        --height 100 \
        --num-objects 2 \
        --max-stacks 2 \
        --use-gpu 1
