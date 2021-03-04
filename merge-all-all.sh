#!/bin/bash



parallel --line-buffer -v ./merge-npz.py --out blocks-{1}-{2}.npz blocks-{1}/*-{2}.npz ::: {3..6} ::: objs bgnd flat high
