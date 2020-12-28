import random

properties         = {}

def random_dict(dict):
  return random.choice(list(dict.items()))


class Unstackable(Exception):
  pass


class Block(object):
  def __init__(self):
    shape_name, self.shape = random_dict(properties['shapes'])
    _, self.color          = random_dict(properties['colors'])
    _, self.size           = random_dict(properties['sizes'])
    _, self.material       = random_dict(properties['materials'])
    self.rotation          = 360.0 * random.random()
    self.stackable         = properties['stackable'][shape_name] == 1
    self.location          = [0,0,0]
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
    return \
      (o1.shape == o2.shape and o1.size == o2.size) or \
      (o1.color == o2.color)

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
        obj = Block()
        ok = True
        for o2 in objects:
          if obj == o2:
            ok = False
            break
        if ok:
          break
      objects.append(obj)

    self.table_size = args.table_size
    self.objects = objects
    self.shuffle()
    pass

  def for_rendering(self):
    return [ vars(o) for o in self.objects ]

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
    unit = max(*list(properties['sizes'].values()))
    max_x = unit * 2 * self.table_size

    if force_change:
      object_below = self.object_just_below(oi)

    trial = 0
    fail = True
    while fail and trial < 100:
      fail = False
      oi.x = max_x * ((random.randint(0,self.table_size-1) / (self.table_size-1)) - 1/2) + random.gauss(0.0, 0.05 * unit)
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

