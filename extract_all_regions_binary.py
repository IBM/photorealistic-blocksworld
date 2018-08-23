#!/usr/bin/env python3

import numpy as np
import json
import imageio
import os
import skimage.transform
import argparse

parser = argparse.ArgumentParser(
    description='extract the regions and save the results in a npz file.')
parser.add_argument('dir')
parser.add_argument('--out', type=argparse.FileType('wb'), default='regions.npz')
parser.add_argument('--maxobj', type=int, default=10)
parser.add_argument('--resized', type=int, default=15)
parser.add_argument('--compress', default=True, action='store_true')

def main(args):

    directory = args.dir
    out       = args.out
    maxobj    = args.maxobj
    resized   = args.resized
    compress  = args.compress

    scenes=os.path.join(directory,"scene_tr")
    files = os.listdir(scenes)
    filenum = len(files)

    images = np.zeros((filenum, maxobj, resized, resized, 3), dtype=np.uint8)
    bboxes = np.zeros((filenum, maxobj, 4), dtype=np.uint16)

    picsize = None
    
    for i,scenefile in enumerate(files):
        if 0==(i%100):
            print(i,"/",filenum)
        
        with open(os.path.join(scenes,scenefile), 'r') as f:
            scene = json.load(f)

        imagefile = os.path.join(directory,"image",scene["image_filename"])
        image = imageio.imread(imagefile)[:,:,:3]
        if picsize is None:
            picsize = image.shape
        
        for j, obj in enumerate(scene["objects"]):
            bbox = tuple(obj["bbox"])
            x1, y1, x2, y2 = bbox
            region = image[int(y1):int(y2), int(x1):int(x2), :]
            images[i,j] = skimage.transform.resize(region,(resized,resized,3),preserve_range=True)
            bboxes[i,j] = bbox

    if compress:
        np.savez_compressed(out,images=images,bboxes=bboxes,picsize=picsize)
    else:
        np.savez(out,images=images,bboxes=bboxes,picsize=picsize)

if __name__ == '__main__':
    import sys
    args = parser.parse_args()
    main(args)

    
        
