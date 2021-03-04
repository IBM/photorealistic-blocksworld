#!/bin/bash



parallel --line-buffer -v ./merge-npz.py --out monoblocks-{1}-{2}.npz monoblocks-{1}/*-{2}.npz ::: {3..6} ::: objs bgnd flat high
