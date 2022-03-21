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

  # Output settings
  blocks.initialize_parser_output_options(parser,prefix='CLEVR')

  parser.add_argument('--start-idx', default=0, type=int,
                      help="The index at which to start for numbering rendered images. Setting " +
                      "this to non-zero values allows you to distribute rendering across " +
                      "multiple machines and recombine the results later.")

  parser.add_argument('--num-transitions', default=100, type=int,
                      help="The number of transitions to render")

  parser.add_argument('--num-samples-per-state', default=5, type=int,
                      help="The number of images to render per logical states")

  # Rendering options
  blocks.initialize_parser_rendering_options(parser)

  return parser


def main(args):
  import copy
  load_colors(args)

  image_prefix = os.path.join(args.output_dir,"image_tr",args.filename_prefix)
  scene_prefix = os.path.join(args.output_dir,"scene_tr",args.filename_prefix)
  os.makedirs(os.path.split(image_prefix)[0], exist_ok=True)
  os.makedirs(os.path.split(scene_prefix)[0], exist_ok=True)

  print("rendering images")
  for i in range(args.start_idx,
                 args.start_idx+args.num_transitions):

    while True:
      try:
        pre = State(args)
        print(json.dumps(pre.for_rendering(),indent=2))

        suc = copy.deepcopy(pre)
        suc.random_action()
        print(json.dumps(suc.for_rendering(),indent=2))

        for j in range(args.num_samples_per_state):
          state = copy.deepcopy(pre)
          state.wiggle()
          render_scene(args,
                       output_image = image_prefix+"_{:06d}_pre_{:03d}.png".format(i,j),
                       output_scene = scene_prefix+"_{:06d}_pre_{:03d}.json".format(i,j),
                       objects      = state.for_rendering())

        for j in range(args.num_samples_per_state):
          state = copy.deepcopy(suc)
          state.wiggle()
          render_scene(args,
                       output_image = image_prefix+"_{:06d}_suc_{:03d}.png".format(i,j),
                       output_scene = scene_prefix+"_{:06d}_suc_{:03d}.json".format(i,j),
                       objects      = state.for_rendering(),
                       action       = state.last_action)
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

