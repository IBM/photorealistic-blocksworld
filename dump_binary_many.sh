#!/bin/bash -x


dir=blocks-3-3-multi

parallel -j 32 ./dump_binary.py --out $dir/{}-globalonly.npz $dir/{} ::: {1..100}

./merge-npz.py --out $dir/$dir-globalonly.npz $dir/{1..100}-globalonly.npz

