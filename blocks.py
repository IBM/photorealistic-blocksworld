import json
import random
from datetime import datetime as dt

properties         = {}

def load_colors(args):
  # Load the property file
  with open(args.properties_json, 'r') as f:
    properties.update(json.load(f))

    # changes color value range from 0-255 to 0-1
    properties["colors"] = [
      tuple(float(c) / 255.0 for c in rgb) + (1.0,) \
      for rgb in properties['colors']
    ]

    if not args.randomize_colors:
      # extract exactly the same numbr of colors as the objects
      # from the top in the order as written in the json file
      properties["colors"] = properties["colors"][:args.num_objects]

  return



def initialize_parser_input_options(parser):
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
  parser.add_argument('--randomize-colors', action="store_true",
                      help="Select the object color from all colors available in properties.json for each state."
                      +" If not present, the list of colors is truncated to match the number of objects"
                      +" during the initialization.")
  parser.add_argument('--allow-duplicates', action="store_true",
                      help="Allow duplicate objects")


def initialize_parser_environment_options(parser):
  # Settings for objects
  parser.add_argument('--num-objects', default=4, type=int,
                      help="The number of objects to place in each scene")

  parser.add_argument('--table-size', default=5, type=int,
                      help="The approximate table size relative to the large object size * 1.5.")

  parser.add_argument('--object-jitter', default=0.0, type=float,
                      help="The magnitude of random jitter to add to the x,y position of each block.")

def initialize_parser_output_options(parser,prefix):
  parser.add_argument('--filename-prefix', default=prefix,
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

def initialize_parser_rendering_options(parser):
  # Rendering options
  parser.add_argument('--use-gpu', default=0, type=int,
                      help="Setting --use-gpu 1 enables GPU-accelerated rendering using CUDA. " +
                      "You must have an NVIDIA GPU with the CUDA toolkit installed for " +
                      "to work.")
  parser.add_argument('--width', default=320, type=int,
                      help="The width (in pixels) for the rendered images")
  parser.add_argument('--height', default=240, type=int,
                      help="The height (in pixels) for the rendered images")
  parser.add_argument('--key-light-jitter', default=0.0, type=float,
                      help="The magnitude of random jitter to add to the key light position.")
  parser.add_argument('--fill-light-jitter', default=0.0, type=float,
                      help="The magnitude of random jitter to add to the fill light position.")
  parser.add_argument('--back-light-jitter', default=0.0, type=float,
                      help="The magnitude of random jitter to add to the back light position.")
  parser.add_argument('--camera-jitter', default=0.0, type=float,
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


def random_dict(dict):
  return random.choice(list(dict.items()))


class Unstackable(Exception):
  pass


class Block(object):
  def __init__(self,i):
    shape_name, self.shape = random_dict(properties['shapes'])
    self.color             = random.choice(properties['colors'])
    _, self.size           = random_dict(properties['sizes'])
    _, self.material       = random_dict(properties['materials'])
    self.rotation          = 360.0 * random.random()
    self.stackable         = properties['stackable'][shape_name] == 1
    self.location          = [0,0,0]
    self.id                = i
    pass

  @property
  def x(self):
    return self.location[0]

  @property
  def y(self):
    return self.location[1]

  @property
  def z(self):
    return self.location[2]

  @x.setter
  def x(self,newvalue):
    self.location[0] = newvalue

  @y.setter
  def y(self,newvalue):
    self.location[1] = newvalue

  @z.setter
  def z(self,newvalue):
    self.location[2] = newvalue

  def __eq__(o1,o2):
    if o1 is None:
      return False
    if o2 is None:
      return False
    return o1.id == o2.id

  def similar(o1,o2):
    if o1 is None:
      return False
    if o2 is None:
      return False
    return \
      o1.color == o2.color and \
      o1.size  == o2.size  and \
      o1.material == o2.material

  def overlap(o1, o2):
    return (abs(o1.x - o2.x) < (o1.size + o2.size))

  def stable_on(o1, o2):
    return (abs(o1.x - o2.x) < o2.size)

  def above(o1, o2):
    return o1.overlap(o2) and (o1.z > o2.z)


class State(object):
  "Randomly select a list of objects while avoiding duplicates"

  def __init__(self,args):
    objects         = []
    for i in range(args.num_objects):
      while True:
        o1 = Block(i)
        if args.allow_duplicates:
          break
        ok = True
        for o2 in objects:
          if o1.similar(o2):
            ok = False
            print("duplicate object!")
            break
        if ok:
          break
      objects.append(o1)

    self.table_size = args.table_size
    self.object_jitter = args.object_jitter
    self.objects = objects
    self.shuffle()
    pass

  def for_rendering(self):
    return [ vars(o) for o in sorted(self.objects, key=(lambda o: o.id)) ]

  def shuffle(self):
    """destructively modify the list of objects using shuffle1."""
    objs = self.objects.copy()
    self.objects.clear()
    for oi in objs:
      self.shuffle1(oi)
      self.objects.append(oi)

  def shuffle1(self,oi,force_change=False):
    """destructively modify an object by choosing a random x position and put it on top of existing objects.
 oi itself is not inserted to the list of objects."""
    # note: if a cube is rotated by 45degree, it should consume 1.41 times the size
    unit = max(properties['sizes'].values())
    max_x = unit * 2 * self.table_size

    if force_change:
      object_below = self.object_just_below(oi)

    trial = 0
    fail = True
    while fail and trial < 100:
      fail = False
      oi.x = max_x * ((random.randint(0,self.table_size-1) / (self.table_size-1)) - 1/2) + random.gauss(0.0, self.object_jitter * unit)
      oi.z = 0
      for oj in self.objects:
        if oi.overlap(oj):
          if not oj.stackable:
            fail = True
            break
          if not oi.stable_on(oj):
            fail = True
            break
          oi.z = max(oi.z, oj.z + oj.size)
      oi.z += oi.size
      if force_change:
        new_object_below = self.object_just_below(oi)
        if object_below == new_object_below:
          # is not shuffled!
          fail = True
      trial += 1

    if fail:
      raise Unstackable("this state is not stackable")
    pass

  def tops(self):
    """returns a list of objects on which nothing is on top of, i.e., it is the top object of the tower."""
    tops = []
    for o1 in self.objects:
      top = True
      for o2 in self.objects:
        if o1 == o2:
          continue
        if o2.above(o1):
          top = False
          break
      if top:
        tops.append(o1)
    return tops

  def objects_below(self,o):
    results = []
    for other in self.objects:
      if o != other and o.above(other):
        results.append(other)
    return results

  def object_just_below(self,o):
    objects_below = self.objects_below(o)
    if len(objects_below) == 0:
      return None
    else:
      result = objects_below[0]
      for other in objects_below[1:]:
        if result.z < other.z:
          result = other
      return result

  def random_action(self):
    method = random.choice([self.action_move])
    method()
    # storing the name of the action. This is visible in the json file
    self.last_action = method.__name__
    pass

  def action_move(self):
    o = random.choice(self.tops())
    index = self.objects.index(o)
    self.objects.remove(o)
    self.shuffle1(o,force_change=True)
    self.objects.insert(index,o)
    # note: do not change the order of the object.
    pass

  def action_change_material(self):
    o = random.choice(self.tops())
    tmp = list(properties['materials'].values())
    tmp.remove(o.material)
    o.material = random.choice(tmp)
    pass

