#!/bin/bash -x

# blender -noaudio \
#         --background --python render_all_images.py -- \
#         --render-num-samples 200 \
#         --output-dir output-3-3-single \
#         --width 150 \
#         --height 100 \
#         --num-objects 3 \
#         --max-stacks 3 \
#         --use-gpu 1 --dry-run
# 
# 480 states
# 2592 transitions

jbsub -mem 4g -cores 1+1 -queue x86_1h -proj $(date -Iminutes) \
      "blender -noaudio \
        --background --python render_all_images.py -- \
        --render-num-samples 200 \
        --output-dir output-3-3-single \
        --width 150 \
        --height 100 \
        --num-objects 3 \
        --max-stacks 3 \
        --use-gpu 1 ; ./extract_all_regions_binary.py --out blocksworld-3-3.npz output-3-3-single/"
