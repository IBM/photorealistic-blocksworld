#!/bin/bash

echo "this test will just render the first 5 images of 2 objs, 2 stacks blocksworld."
read -n 1 -s -r -p "Press any key to continue"

blender -noaudio --background --python render_images.py -- \
      --output-dir      output                          \
      --initial-objects output-init.json                \
      --statistics      output-stat.json                \
      --render-num-samples 50                           \
      --num-images         5                            \
      --start-idx          0                            \
      --width 300                                       \
      --height 200                                      \
      --num-objects 2                                   \
      --max-stacks  2


# ./extract_region.py output/scenes/CLEVR_new_000000_pre.json
# ./extract_region.py output/scenes/CLEVR_new_000000_suc.json
