#!/bin/bash -x


dir=blocks-3-3-multi

parallel -j 16 ./extract_all_regions_binary.py --include-background --out $dir/{}-global.npz $dir/{} ::: {1..100}

./merge-npz.py --out $dir/$dir-global.npz $dir/{1..100}-global.npz

