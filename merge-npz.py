#!/usr/bin/env python3

import numpy as np
import argparse
import tqdm

parser = argparse.ArgumentParser(description='merge npz files.')

parser.add_argument('--out', default='regions.npz', help="output npz pathname.")
parser.add_argument('npzs', nargs="+", help="list of npz files to be merged.")

args = parser.parse_args()

print("merging npzs")
_images_mean = []
_images_var = []
_bboxes_mean = []
_bboxes_var = []
_transitions = []

with np.load(args.npzs[0]) as data:
    picsize = data['picsize']

count = 0
for npz in tqdm.tqdm(args.npzs):
    with np.load(npz) as data:
        l = len(data["images_mean"])
        if (l % 2) != 0:
            print(f"This run is terminated prematurely! number of images == {l} must be even. Discarding the final data point.")
            l -= 1

        # [:l] ignores the final data point when the dataset contains an odd number of elements
        _images_mean.append(data["images_mean"][:l])
        _images_var.append(data["images_var"][:l])
        _bboxes_mean.append(data["bboxes_mean"][:l])
        _bboxes_var.append(data["bboxes_var"][:l])
        _transitions.append(data["transitions"][:l]+count) # shift the state id
        count += l

with open(args.out, mode="w+b") as f:
    np.savez_compressed(f,
                        images_mean=np.concatenate(_images_mean,axis=0),
                        images_var=np.concatenate(_images_var,axis=0),
                        bboxes_mean=np.concatenate(_bboxes_mean,axis=0),
                        bboxes_var=np.concatenate(_bboxes_var,axis=0),
                        picsize=picsize,
                        transitions=np.concatenate(_transitions,axis=0))
    f.truncate()
