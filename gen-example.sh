#!/bin/bash

blenderdir=$(echo blender-2.*/)
$blenderdir/blender -noaudio --background --python render_images.py -- \
      --output-dir      example                         \
      --statistics      exampl-stat.json                \
      --render-num-samples 300                          \
      --num-images         1                            \
      --start-idx          10000                        \
      --width 800                                       \
      --height 600                                      \
      --num-objects 7

