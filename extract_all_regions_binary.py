#!/usr/bin/env python3

import numpy as np
import json
import imageio
import os.path
import skimage.transform
import skimage.exposure
import skimage.color
from skimage.util import img_as_float, img_as_ubyte
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
parser.add_argument('--preprocess', action='store_true',
                    help="Normalize the image using histogram normalization (images are converted to ycbcr, y channel is normalzied, then put back to rgb.")
parser.add_argument('--preprocess-mode', type=int, default=6,
                    help="")
parser.add_argument('--resize-image', action="store_true",
                    help="When this flag is set, just resize the image and put the results in the parent directory.")
parser.add_argument('--num-samples-per-state', default=5, type=int,
                    help="The number of images to render per logical states")


def preprocess(mode,rgb):
    if mode == 0:
        return rgb
    elif mode == 1:
        yuv = skimage.color.rgb2yuv(rgb)
        yuv[:,:,0] = skimage.exposure.equalize_hist(yuv[:,:,0])
        return np.clip(skimage.color.yuv2rgb(yuv),0.0,1.0)
    elif mode == 2:
        return skimage.exposure.equalize_hist(rgb)
    elif mode == 3:
        return skimage.exposure.equalize_adapthist(rgb)
    elif mode == 4:
        return skimage.exposure.rescale_intensity(im)
    elif mode == 5:
        hsv = skimage.color.rgb2hsv(rgb)
        hsv[:,:,1] = skimage.exposure.rescale_intensity(hsv[:,:,1])
        return skimage.color.hsv2rgb(hsv)
    elif mode == 6:
        hsv = skimage.color.rgb2hsv(rgb)
        hsv[:,:,1] = skimage.exposure.rescale_intensity(hsv[:,:,1])
        hsv[:,:,2] = skimage.exposure.rescale_intensity(hsv[:,:,2])
        return skimage.color.hsv2rgb(hsv)



def path(dir,i,presuc,j,ext):
    return os.path.join(args.dir,dir,"CLEVR_{:06d}_{}_{}.{}".format(i,presuc,j,ext))


def main(args):

    if args.resize_image:
        save_as_resize(args)
        return

    scenes=os.path.join(args.dir,"scene_tr")
    files = os.listdir(scenes)
    files.sort()
    filenum = len(files)

    with open(os.path.join(scenes,files[0]), 'r') as f:
        scene = json.load(f)
        maxobj = len(scene["objects"])
        imagefile = os.path.join(args.dir,"image_tr",scene["image_filename"])
        image = imageio.imread(imagefile)[:,:,:3]
        picsize = image.shape

    if not args.as_problem:
        # .../CLEVR_000000_pre_000.png
        start_idx = int(os.path.split(imagefile)[1].split("_")[1])

    if args.exclude_objects:
        maxobj = 0
    if args.include_background:
        maxobj += 1

    images = np.zeros((filenum, *picsize), dtype=np.uint8)
    patches = np.zeros((filenum, maxobj, *args.resize, 3), dtype=np.uint8)
    bboxes = np.zeros((filenum, maxobj, 4), dtype=np.uint16)

    if args.include_background:
        # picsize = (200, 300, 3)
        # [0,0,300,200] --- xmin,ymin,xmax,ymax
        bboxes[:,-1] = [0,0,picsize[1],picsize[0]]

    print("extracting images")
    # store states
    for i,scenefile in tqdm.tqdm(enumerate(files),total=len(files)):

        with open(os.path.join(scenes,scenefile), 'r') as f:
            scene = json.load(f)

        imagefile = os.path.join(args.dir,"image_tr",scene["image_filename"])
        image_ubyte = imageio.imread(imagefile)[:,:,:3] # range: [0,   255]
        image = img_as_float(image_ubyte)               # range: [0.0, 1.0]
        if args.preprocess:
            image = preprocess(args.preprocess_mode,image)
        assert(picsize==image.shape)
        images[i] = image_ubyte
        if args.include_background:
            # note: resize may cause numerical error that makes values exceed 0.0,1.0.
            # the value is now from 0 to 255.
            patches[i,-1] = img_as_ubyte(np.clip(skimage.transform.resize(image,(*args.resize,3)), 0.0, 1.0))
        if args.exclude_objects:
            continue

        for j, obj in enumerate(scene["objects"]):
            bbox = tuple(obj["bbox"])
            x1, y1, x2, y2 = bbox
            region = image[int(y1):int(y2), int(x1):int(x2), :]
            # note: resize may cause numerical error that makes values exceed 0.0,1.0
            patches[i,j] = img_as_ubyte(np.clip(skimage.transform.resize(region,(*args.resize,3)), 0.0, 1.0))
            bboxes[i,j] = bbox

    if args.as_problem:
        save_as_problem(args.out,patches,bboxes,picsize)
        return

    print("computing means and variances")
    samples = args.num_samples_per_state
    num_states = filenum // samples
    num_transitions = num_states // 2
    images = images.reshape((num_states, samples, *picsize))
    patches = patches.reshape((num_states, samples, maxobj, *args.resize, 3))
    bboxes = bboxes.reshape((num_states, samples, maxobj, 4))
    images_mean = images.mean(axis=1) # [0, 2^8-1]
    patches_mean = patches.mean(axis=1)
    bboxes_mean = bboxes.mean(axis=1)
    images_std = images.std(axis=1) # [0, 2^8-1]
    patches_std = patches.std(axis=1)
    bboxes_std = bboxes.std(axis=1)
    images_var = images.var(axis=1) # [0, 2^16-1]
    patches_var = patches.var(axis=1)
    bboxes_var = bboxes.var(axis=1)

    images_mean2 = images_mean.reshape((num_transitions, 2, *picsize))
    images_std2  = images_std.reshape((num_transitions, 2, *picsize))
    os.makedirs(os.path.join(args.dir,"distr_tr"),exist_ok=True)
    for i in tqdm.tqdm(range(num_transitions)):
        for presuc,j in (("pre",0),("suc",1)):
            imageio.imwrite(path("distr_tr",start_idx+i,presuc,"mean","png"), img_as_ubyte(images_mean2[i,j]/255))
            imageio.imwrite(path("distr_tr",start_idx+i,presuc,"std","png"), img_as_ubyte(images_std2[i,j]/255))

    np.savez_compressed(args.out,
                        images_mean=patches_mean.astype(np.uint8),
                        images_var=patches_var.astype(np.uint16),
                        bboxes_mean=bboxes_mean.astype(np.uint16),
                        bboxes_var=bboxes_var.astype(np.uint32),
                        picsize=picsize,
                        # store state ids
                        transitions=np.arange(num_states, dtype=np.uint32))
    pass

def save_as_problem(out,images,bboxes,picsize):
    assert len(images) == 2
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



def save_as_resize(args):
    for name in ["init.png", "goal.png"]:
        imagefile = os.path.join(args.dir,"image_tr",name)
        image = img_as_float(imageio.imread(imagefile)[:,:,:3])
        image = img_as_ubyte(np.clip(skimage.transform.resize(image,(*args.resize,3)), 0.0, 1.0))
        imageio.imwrite(os.path.join(args.dir,name), image)
    pass


if __name__ == '__main__':
    import sys
    args = parser.parse_args()
    main(args)



