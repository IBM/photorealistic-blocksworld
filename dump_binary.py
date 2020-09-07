#!/usr/bin/env python3

import numpy as np
import json
import imageio
import os.path
import skimage.transform
import argparse
import tqdm

parser = argparse.ArgumentParser(
    description='just store the entire images in a npz file.')
parser.add_argument('dir')
parser.add_argument('--out', type=argparse.FileType('wb'), default='regions.npz')
parser.add_argument('--resize', type=int, default=96,
                    # the choise of default value is so that the dimension is still a multiple of 32
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
        imagefile = os.path.join(directory,"image",scene["image_filename"])
        image = imageio.imread(imagefile)[:,:,:3]
        picsize = image.shape

    shape = (resize, int(picsize[1]*resize/picsize[0]),3)
    images = np.zeros((filenum, 1, *shape), dtype=np.uint8)
    bboxes = np.zeros((filenum, 1, 4), dtype=np.uint16)
    bboxes[:,0] = [0,0,picsize[1],picsize[0]] # x1,y1,x2,y2

    # store states
    for i,scenefile in tqdm.tqdm(enumerate(files)):

        with open(os.path.join(scenes,scenefile), 'r') as f:
            scene = json.load(f)

        imagefile = os.path.join(directory,"image",scene["image_filename"])
        image = imageio.imread(imagefile)[:,:,:3]
        image = skimage.transform.resize(image, shape, preserve_range=True)
        images[i,0] = image

    # store transitions
    scenes=os.path.join(directory,"scene_tr")
    files = os.listdir(scenes)
    files.sort()
    filenum = len(files)

    transitions = np.zeros(filenum, dtype=np.uint32)
    for i,scenefile in tqdm.tqdm(enumerate(files)):

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

