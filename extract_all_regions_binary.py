#!/usr/bin/env python3

import numpy as np
import json
import imageio
import os.path
import skimage.transform
import argparse

parser = argparse.ArgumentParser(
    description='extract the regions and save the results in a npz file.')
parser.add_argument('dir')
parser.add_argument('--out', type=argparse.FileType('wb'), default='regions.npz')
parser.add_argument('--resize', type=int, default=32,
                    help="the size of the image patch resized from the region originally extracted")

def main(args):

    directory = args.dir
    out       = args.out
    resize   = args.resize

    scenes=os.path.join(directory,"scene")
    files = os.listdir(scenes)
    files.sort()
    filenum = len(files)

    with open(os.path.join(scenes,files[0]), 'r') as f:
        scene = json.load(f)
        maxobj = len(scene["objects"])
        imagefile = os.path.join(directory,"image",scene["image_filename"])
        image = imageio.imread(imagefile)[:,:,:3]
        picsize = image.shape

    images = np.zeros((filenum, maxobj, resize, resize, 3), dtype=np.uint8)
    bboxes = np.zeros((filenum, maxobj, 4), dtype=np.uint16)

    # store states
    for i,scenefile in enumerate(files):
        if 0==(i%100):
            print(i,"/",filenum)
        
        with open(os.path.join(scenes,scenefile), 'r') as f:
            scene = json.load(f)
            assert(maxobj==len(scene["objects"]))

        imagefile = os.path.join(directory,"image",scene["image_filename"])
        image = imageio.imread(imagefile)[:,:,:3]
        assert(picsize==image.shape)

        for j, obj in enumerate(scene["objects"]):
            bbox = tuple(obj["bbox"])
            x1, y1, x2, y2 = bbox
            region = image[int(y1):int(y2), int(x1):int(x2), :]
            images[i,j] = skimage.transform.resize(region,(resize,resize,3),preserve_range=True)
            bboxes[i,j] = bbox
    
    # store transitions
    scenes=os.path.join(directory,"scene_tr")
    files = os.listdir(scenes)
    files.sort()
    filenum = len(files)
    
    transitions = np.zeros(filenum, dtype=np.uint32)
    for i,scenefile in enumerate(files):
        if 0==(i%100):
            print(i,"/",filenum)
        
        with open(os.path.join(scenes,scenefile), 'r') as f:
            scene = json.load(f)
        
        imagefile = scene["image_filename"]
        # CLEVR_new_000000.png
        name, _ = os.path.splitext(imagefile)
        index = int(name.split("_")[2])
        transitions[i] = index
    
    np.savez_compressed(out,images=images,bboxes=bboxes,picsize=picsize,transitions=transitions)

if __name__ == '__main__':
    import sys
    args = parser.parse_args()
    main(args)

    
        
