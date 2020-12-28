#!/usr/bin/env python3

import numpy as np
import argparse
import tqdm

parser = argparse.ArgumentParser(description='merge npz files.')

parser.add_argument('--out', type=argparse.FileType('wb'), default='regions.npz', help="output npz pathname.")
parser.add_argument('npzs', nargs="+", help="list of npz files to be merged.")

args = parser.parse_args()

_images = []
_bboxes = []
_transitions = []

with np.load(args.npzs[0]) as data:
    picsize = data['picsize']

count = 0
for npz in tqdm.tqdm(args.npzs):
    with np.load(npz) as data:
        l = len(data["images"])
        if (l % 2) != 0:
            print(f"This run is terminated prematurely! number of images == {l}")
            l -= 1

        _images.append(data["images"][:l])
        _bboxes.append(data["bboxes"][:l])
        _transitions.append(data["transitions"][:l]+count)
        count += l

np.savez_compressed(args.out,
                    images=np.concatenate(_images,axis=0),
                    bboxes=np.concatenate(_bboxes,axis=0),
                    picsize=picsize,
                    transitions=np.concatenate(_transitions,axis=0))
