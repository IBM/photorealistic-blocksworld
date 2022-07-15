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
parser.add_argument('--num-samples-per-state', default=5, type=int,
                    help="The number of images to render per logical states")


def preprocess(args,rgb):
    if not args.preprocess:
        args.preprocess_mode = 0
    mode = args.preprocess_mode
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


def safe_load_json(path):
    with open(path, 'r+') as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError as e:
            # HACK HACK: temporary solution to ignore extraneous data at the end of file
            # caused by open(path, "w") instead of open(path, "w+").
            # Seek it back the beginning of file, read a string until the errored position, then parse it
            print("while parsing", path, ":")
            print(e)
            f.seek(0)
            obj = json.loads(f.read(e.pos))
            print("truncating",path)
            f.seek(e.pos)
            f.truncate()
            return obj


def main(args):

    scenes=os.path.join(args.dir,"scene_tr")
    files = [ f for f in os.listdir(scenes) if "---" not in f ]
    files.sort()
    filenum = len(files)

    scene = safe_load_json(os.path.join(scenes,files[0]))
    maxobj = len(scene["objects"])
    imagefile = os.path.join(args.dir,"image_tr",scene["image_filename"])
    image = imageio.imread(imagefile)[:,:,:3]
    picsize = image.shape

    # .../CLEVR_XXXXXX_pre_YYY.png -> XXXXXX
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

        scene = safe_load_json(os.path.join(scenes,scenefile))

        imagefile = os.path.join(args.dir,"image_tr",scene["image_filename"])
        image_ubyte = imageio.imread(imagefile)[:,:,:3] # range: [0,   255]
        image = img_as_float(image_ubyte)               # range: [0.0, 1.0]
        image = preprocess(args,image)
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

    if args.as_problem:
        save_as = save_as_problem
    else:
        save_as = save_as_dataset
    save_as(args,samples,num_states,num_transitions,
            patches_mean,patches_var,
            bboxes_mean,bboxes_var,
            picsize)

    pass

def save_as_dataset(args,
                    samples,num_states,num_transitions,
                    patches_mean,patches_var,
                    bboxes_mean,bboxes_var,
                    picsize):

    np.savez_compressed(args.out,
                        # note: the name mismatch (images vs patches) is not a mistake,
                        # an artifact of history of changes.
                        images_mean=patches_mean.astype(np.uint8),
                        images_var=patches_var.astype(np.uint16),
                        bboxes_mean=bboxes_mean.astype(np.uint16),
                        bboxes_var=bboxes_var.astype(np.uint32),
                        # metadata
                        picsize=picsize,
                        patch_shape=[*args.resize,3],
                        num_samples_per_state=args.num_samples_per_state,
                        # store state ids
                        transitions=np.arange(num_states, dtype=np.uint32))
    args.out.truncate()


def save_as_problem(args,
                    samples,num_states,num_transitions,
                    patches_mean,patches_var,
                    bboxes_mean,bboxes_var,
                    picsize):

    B,O,H,W,C = patches_mean.shape
    patches_mean = patches_mean.reshape((B,O,H*W*C)) / 255
    patches_var  = patches_var.reshape((B,O,H*W*C)) / (255*255)
    coords_mean = bboxes_to_coord(bboxes_mean,"mean")
    coords_var = bboxes_to_coord(bboxes_var,"variance")
    states_mean = np.concatenate((patches_mean,coords_mean),axis=-1)
    states_var = np.concatenate((patches_var,coords_var),axis=-1)
    states = np.concatenate((states_mean,states_var),axis=-1)
    init,goal = states
    np.savez_compressed(args.out,
                        init=init,
                        goal=goal,
                        # metadata
                        picsize=picsize,
                        patch_shape=[*args.resize,3],
                        num_samples_per_state=args.num_samples_per_state,)
    args.out.truncate()



def bboxes_to_coord(bboxes,mode="mean"):
    assert mode in ("mean", "variance")
    if mode == "mean":
        coord1, coord2 = bboxes[...,0:2], bboxes[...,2:4]
        center, width = (coord2+coord1)/2, (coord2-coord1)/2
        return np.concatenate((center,width),axis=-1)
    else:
        # Var(-X) == Var(X)
        # Var(X+Y) == Var(X) + Var(Y) for independent variables
        # Var(aX) == a^2 Var(X)
        # so Var(X+Y / 2) = Var(X)+Var(Y) / 4
        coord1, coord2 = bboxes[...,0:2], bboxes[...,2:4]
        center, width = (coord2+coord1)/4, (coord2+coord1)/4
        return np.concatenate((center,width),axis=-1)



if __name__ == '__main__':
    import sys
    args = parser.parse_args()
    main(args)



