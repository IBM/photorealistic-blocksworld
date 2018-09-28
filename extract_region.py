#!/usr/bin/env python3

"Extract the regions from a scene json file"

import numpy as np
import json
import imageio
import os

def main(scenefile):
    with open(scenefile, 'r') as f:
        scene = json.load(f)

    base, nameext = os.path.split(scenefile)
    name, ext     = os.path.splitext(nameext)
    # print(base,nameext,name,ext)
    assert(ext==".json")
    
    imagefile_base = os.path.join("{}/../images/{}".format(base,name))
    image = imageio.imread(imagefile_base+".png")
    # print(image.shape)
    
    for i, obj in enumerate(scene["objects"]):
        bbox = tuple(obj["bbox"])
        # print(bbox)
        x1, y1, x2, y2 = bbox
        region = image[int(y1):int(y2), int(x1):int(x2), :]
        imageio.imwrite("{}_{}.png".format(imagefile_base,i),region)

if __name__ == '__main__':
    import sys
    main(*sys.argv[1:])

    
        
