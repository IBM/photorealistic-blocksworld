#!/usr/bin/env python3

import numpy as np
import argparse
import tqdm

parser = argparse.ArgumentParser(description='merge npz files.')

parser.add_argument('--out', type=argparse.FileType('wb'), default='regions.npz')
parser.add_argument('npzs', nargs="+")

args = parser.parse_args()

_images = []
_bboxes = []
_transitions = []

with np.load(args.npzs[0]) as data:
    picsize = data['picsize']

for npz in tqdm.tqdm(args.npzs):
    with np.load(npz) as data:
        _images.append(data["images"])
        _bboxes.append(data["bboxes"])
        _transitions.append(data["transitions"])

np.savez_compressed(args.out,
                    images=np.concatenate(_images,axis=0),
                    bboxes=np.concatenate(_bboxes,axis=0),
                    picsize=picsize,
                    transitions=np.concatenate(_transitions,axis=0))
