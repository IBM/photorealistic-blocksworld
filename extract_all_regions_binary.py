#!/usr/bin/env python3

import numpy as np
import json
import imageio
import os.path
import skimage.transform
import skimage.exposure
import skimage.color
import argparse
import tqdm

parser = argparse.ArgumentParser(
    description='extract the regions and save the results in a npz file.')
parser.add_argument('dir')
parser.add_argument('--out', type=argparse.FileType('wb'), default='regions.npz')
parser.add_argument('--resize', type=int, default=(32,32), nargs=2, metavar=("Y","X"),
                    help="the size of the image patch resized from the region originally extracted")
parser.add_argument('--exclude-objects', action='store_true',
                    help="do not include object representations in the output.")
parser.add_argument('--include-background', action='store_true',
                    help="include the whole image as a global object. The object is inserted at the end.")
parser.add_argument('--as-problem', action='store_true',
                    help="Store the data into 'init' and 'goal' fields used by the planner instead of the usual set of fields in the archive.")
parser.add_argument('--normalize-histogram', action='store_true',
                    help="Normalize the image using histogram normalization (images are converted to ycbcr, y channel is normalzied, then put back to rgb.")

def color_histogram_normalization(image):
    ycbcr = skimage.color.rgb2ycbcr(image)
    ycbcr[:,:,0] = skimage.exposure.equalize_hist(ycbcr[:,:,0])
    return skimage.color.ycbcr2rgb(image)



def main(args):

    directory = args.dir
    out       = args.out
    resizeY, resizeX   = args.resize

    scenes=os.path.join(directory,"scene_tr")
    files = os.listdir(scenes)
    files.sort()
    filenum = len(files)

    with open(os.path.join(scenes,files[0]), 'r') as f:
        scene = json.load(f)
        maxobj = len(scene["objects"])
        imagefile = os.path.join(directory,"image_tr",scene["image_filename"])
        image = imageio.imread(imagefile)[:,:,:3]
        picsize = image.shape

    if args.exclude_objects:
        maxobj = 0
    if args.include_background:
        maxobj += 1

    images = np.zeros((filenum, maxobj, resizeY, resizeX, 3), dtype=np.uint8)
    bboxes = np.zeros((filenum, maxobj, 4), dtype=np.uint16)

    if args.include_background:
        # picsize = (200, 300, 3)
        # [0,0,300,200] --- xmin,ymin,xmax,ymax
        bboxes[:,-1] = [0,0,picsize[1],picsize[0]]

    # store states
    for i,scenefile in tqdm.tqdm(enumerate(files)):
        
        with open(os.path.join(scenes,scenefile), 'r') as f:
            scene = json.load(f)

        imagefile = os.path.join(directory,"image_tr",scene["image_filename"])
        image = imageio.imread(imagefile)[:,:,:3]
        assert(picsize==image.shape)
        if args.include_background:
            images[i,-1] = skimage.transform.resize(image,(resizeY, resizeX,3),preserve_range=True)
            if args.normalize_histogram:
                images[i,-1] = color_histogram_normalization(images[i,-1])
        if args.exclude_objects:
            continue

        for j, obj in enumerate(scene["objects"]):
            bbox = tuple(obj["bbox"])
            x1, y1, x2, y2 = bbox
            region = image[int(y1):int(y2), int(x1):int(x2), :]
            images[i,j] = skimage.transform.resize(region,(resizeY, resizeX,3),preserve_range=True)
            if args.normalize_histogram:
                images[i,j] = color_histogram_normalization(images[i,j])
            bboxes[i,j] = bbox
    
    # store transitions
    transitions = np.arange(filenum, dtype=np.uint32)

    if not args.as_problem:
        np.savez_compressed(out,images=images,bboxes=bboxes,picsize=picsize,transitions=transitions)
    else:
        assert len(images) == 2
        save_as_problem(out,images,bboxes,picsize)
    pass

def save_as_problem(out,images,bboxes,picsize):
    def bboxes_to_coord(bboxes):
        coord1, coord2 = bboxes[:,:,0:2], bboxes[:,:,2:4]
        center, width = (coord2+coord1)/2, (coord2-coord1)/2
        coords        = np.concatenate((center,width),axis=-1)
        return coords

    B,O,H,W,C = images.shape
    states = images.reshape((B,O,H*W*C)) / 256
    coords = bboxes_to_coord(bboxes)
    states = np.concatenate((states,coords),axis=-1)
    init,goal = states
    np.savez_compressed(out,init=init,goal=goal,picsize=picsize)
    

if __name__ == '__main__':
    import sys
    args = parser.parse_args()
    main(args)

    
        
