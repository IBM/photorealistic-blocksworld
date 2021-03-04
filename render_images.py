# Copyright 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree. An additional grant
# of patent rights can be found in the PATENTS file in the same directory.

from __future__ import print_function
import sys, argparse, json, os
from datetime import datetime as dt
  
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
    from blocks import State, Unstackable
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
  parser.add_argument('--base-scene-blendfile', default='data/base_scene.blend',
                      help="Base blender file on which all scenes are based; includes " +
                      "ground plane, lights, and camera.")
  parser.add_argument('--properties-json', default='data/properties.json',
                      help="JSON file defining objects, materials, sizes, and colors. " +
                      "The \"colors\" field maps from CLEVR color names to RGB values; " +
                      "The \"sizes\" field maps from CLEVR size names to scalars used to " +
                      "rescale object models; the \"materials\" and \"shapes\" fields map " +
                      "from CLEVR material and shape names to .blend files in the " +
                      "--object-material-dir and --shape-dir directories respectively.")
  parser.add_argument('--shape-dir', default='data/shapes',
                      help="Directory where .blend files for object models are stored")
  parser.add_argument('--material-dir', default='data/materials',
                      help="Directory where .blend files for materials are stored")
  parser.add_argument('--allow-duplicates', action="store_true",
                      help="Allow duplicate objects")
  
  # Settings for objects
  parser.add_argument('--num-objects', default=4, type=int,
                      help="The number of objects to place in each scene")

  parser.add_argument('--table-size', default=6, type=int,
                      help="The approximate table size relative to the large object size * 1.5.")
  
  parser.add_argument('--object-jitter', default=0.2, type=int,
                      help="The magnitude of random jitter to add to the x,y position of each block.")
  
  # Output settings
  parser.add_argument('--start-idx', default=0, type=int,
                      help="The index at which to start for numbering rendered images. Setting " +
                      "this to non-zero values allows you to distribute rendering across " +
                      "multiple machines and recombine the results later.")
  parser.add_argument('--num-images', default=100, type=int,
                      help="The number of images to render")
  
  parser.add_argument('--filename-prefix', default='CLEVR',
                      help="This prefix will be prepended to the rendered images and JSON scenes")
  parser.add_argument('--output-dir', default='output',
                      help="The directory where output will be stored. It will be " +
                      "created if it does not exist.")
  parser.add_argument('--save-blendfiles', type=int, default=0,
                      help="Setting --save-blendfiles 1 will cause the blender scene file for " +
                      "each generated image to be stored in the directory specified by " +
                      "the --output-blend-dir flag. These files are not saved by default " +
                      "because they take up ~5-10MB each.")
  parser.add_argument('--version', default='1.0',
                      help="String to store in the \"version\" field of the generated JSON file")
  parser.add_argument('--license',
                      default="Creative Commons Attribution (CC-BY 4.0)",
                      help="String to store in the \"license\" field of the generated JSON file")
  parser.add_argument('--date', default=dt.today().strftime("%m/%d/%Y"),
                      help="String to store in the \"date\" field of the generated JSON file; " +
                      "defaults to today's date")
  
  # Rendering options
  parser.add_argument('--use-gpu', default=0, type=int,
                      help="Setting --use-gpu 1 enables GPU-accelerated rendering using CUDA. " +
                      "You must have an NVIDIA GPU with the CUDA toolkit installed for " +
                      "to work.")
  parser.add_argument('--width', default=320, type=int,
                      help="The width (in pixels) for the rendered images")
  parser.add_argument('--height', default=240, type=int,
                      help="The height (in pixels) for the rendered images")
  parser.add_argument('--key-light-jitter', default=1.0, type=float,
                      help="The magnitude of random jitter to add to the key light position.")
  parser.add_argument('--fill-light-jitter', default=1.0, type=float,
                      help="The magnitude of random jitter to add to the fill light position.")
  parser.add_argument('--back-light-jitter', default=1.0, type=float,
                      help="The magnitude of random jitter to add to the back light position.")
  parser.add_argument('--camera-jitter', default=0.5, type=float,
                      help="The magnitude of random jitter to add to the camera position")
  parser.add_argument('--render-num-samples', default=512, type=int,
                      help="The number of samples to use when rendering. Larger values will " +
                      "result in nicer images but will cause rendering to take longer.")
  parser.add_argument('--render-min-bounces', default=8, type=int,
                      help="The minimum number of bounces to use for rendering.")
  parser.add_argument('--render-max-bounces', default=8, type=int,
                      help="The maximum number of bounces to use for rendering.")
  parser.add_argument('--render-tile-size', default=256, type=int,
                      help="The tile size to use for rendering. This should not affect the " +
                      "quality of the rendered image but may affect the speed; CPU-based " +
                      "rendering may achieve better performance using smaller tile sizes " +
                      "while larger tile sizes may be optimal for GPU-based rendering.")
  return parser


def main(args):
  # Load the property file
  with open(args.properties_json, 'r') as f:
    blocks.properties = json.load(f)
    blocks.properties["colors"] = {
      name : tuple(float(c) / 255.0 for c in rgb) + (1.0,) \
      for name, rgb in blocks.properties['colors'].items()
    }
  
  trans_img_dir   = os.path.join(args.output_dir,"image_tr")
  trans_scene_dir = os.path.join(args.output_dir,"scene_tr")

  for d in [trans_img_dir,
            trans_scene_dir]:
    if not os.path.isdir(d):
      os.makedirs(d)

  template = args.filename_prefix+"_%06d"
  trans_img_template   = os.path.join(trans_img_dir,  template)
  trans_scene_template = os.path.join(trans_scene_dir,template)
  
  for i in range(args.start_idx,
                 args.start_idx+args.num_images):

    i_pre = (trans_img_template   % i)+"_pre.png"
    s_pre = (trans_scene_template % i)+"_pre.json"
    i_suc = (trans_img_template   % i)+"_suc.png"
    s_suc = (trans_scene_template % i)+"_suc.json"

    while True:
      try:
        state = State(args)
        print(json.dumps(state.for_rendering(),indent=2))

        render_scene(args,
                     output_image = i_pre,
                     output_scene = s_pre,
                     objects      = state.for_rendering())

        state.random_action()
        print(json.dumps(state.for_rendering(),indent=2))

        render_scene(args,
                     output_image = i_suc,
                     output_scene = s_suc,
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

