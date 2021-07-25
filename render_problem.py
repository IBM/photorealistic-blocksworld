# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

from __future__ import print_function
import sys, argparse, json, os
  
INSIDE_BLENDER = True
try:
  import bpy, bpy_extras
  from mathutils import Vector
except ImportError as e:
  INSIDE_BLENDER = False
if INSIDE_BLENDER:
  try:
    import utils
    import blocks
    from blocks import State, Unstackable, load_colors
    from render_utils import render_scene
  except ImportError as e:
    print("\nERROR")
    print("Running render_images.py from Blender and cannot import utils.py.") 
    print("You may need to add a .pth file to the site-packages of Blender's")
    print("bundled python with a command like this:\n")
    print("echo $PWD >> $BLENDER/$VERSION/python/lib/python3.5/site-packages/clevr.pth")
    print("\nWhere $BLENDER is the directory where Blender is installed, and")
    print("$VERSION is your Blender version (such as 2.78).")
    sys.exit(1)

def initialize_parser():
  parser = argparse.ArgumentParser()

  # Input options
  blocks.initialize_parser_input_options(parser)

  # Environment options
  blocks.initialize_parser_environment_options(parser)

  # Problem options
  parser.add_argument('--num-steps', default=4, type=int,
                      help="The number of steps to perform from the initial state")

  # Output settings
  blocks.initialize_parser_output_options(parser,prefix='problem')
  
  # Rendering options
  blocks.initialize_parser_rendering_options(parser)

  return parser


def main(args):
  load_colors(args)
  
  trans_img_dir   = os.path.join(args.output_dir,"image_tr")
  trans_scene_dir = os.path.join(args.output_dir,"scene_tr")

  for d in [trans_img_dir,
            trans_scene_dir]:
    if not os.path.isdir(d):
      os.makedirs(d)

  i_pre = os.path.join(trans_img_dir   ,"init.png")
  s_pre = os.path.join(trans_scene_dir ,"init.json")
  i_suc = os.path.join(trans_img_dir   ,"goal.png")
  s_suc = os.path.join(trans_scene_dir ,"goal.json")

  while True:
    try:
      state = State(args)

      render_scene(args,
                   output_image = i_pre,
                   output_scene = s_pre,
                   objects      = state.for_rendering())

      for _ in range(args.num_steps):
        state.action_move()

      render_scene(args,
                   output_image = i_suc,
                   output_scene = s_suc,
                   objects      = state.for_rendering())
      break
    except Unstackable as e:
      print(e)
      pass


if __name__ == '__main__':
  parser = initialize_parser()
  if INSIDE_BLENDER:
    # Run normally
    argv = utils.extract_args()
    args = parser.parse_args(argv)
    main(args)
  elif '--help' in sys.argv or '-h' in sys.argv:
    parser.print_help()
  else:
    print('This script is intended to be called from blender like this:')
    print()
    print('blender --background --python render_images.py -- [args]')
    print()
    print('You can also run as a standalone python script to view all')
    print('arguments like this:')
    print()
    print('python render_images.py --help')

