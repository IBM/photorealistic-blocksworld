
# Photo-Realistic Blocksworld [![Build Status](https://travis-ci.org/IBM/photorealistic-blocksworld.svg?branch=master)](https://travis-ci.org/IBM/photorealistic-blocksworld)

NEWS: `.npz` binaries are available from https://github.com/IBM/photorealistic-blocksworld/releases .

This is a repository modified from the [CLEVR dataset](https://github.com/facebookresearch/clevr-dataset-gen)
for generating realistic visualizations of [blocksworld](https://en.wikipedia.org/wiki/Blocks_world).


Setup:

With anaconda,

```
sudo apt-get install parallel jq
conda env create -f environment.yml
```

Install blender:

```
wget https://download.blender.org/release/Blender2.77/blender-2.77a-linux-glibc211-x86_64.tar.bz2
tar xf blender-2.77a-linux-glibc211-x86_64.tar.bz2
echo $PWD > $(echo blender*/2.*/python/lib/python*/site-packages/)clevr.pth
```

Example: Run `./test.sh`.

For the original readme, see [README-clevr.md](README-clevr.md) .

Note: I changed all keyword options from using underscores to using hyphens (e.g. `--use_gpu` -> `--use-gpu`).

<div align="center">
  <img src="example/image/CLEVR_new_010000.png" width="800px">
</div>

# Functionality

+ `render_images.py` : 
  
  Renders all possible states of the blocks world and dump the metadata
  (e.g. bounding boxes) in the corresponding json files.
  This file runs under the python distribution included in the blender.

+ `extract_region.py` :

  Extract each region that contains an object from an image and store them in
  png files. Takes a metadata json file as the input.
  This file runs in the conda environment.

+ `extract_all_regions_binary.py` :

  Extract the regions from the every images generated, resize them to 32x32 and
  store them in a `.npz` container along with the bounding box vector (x1,y1,x2,y2).
  This file runs in the conda environment.

# Running

To generate a small dataset with 2 blocks / 2 stacks:

    ./generate_all.sh 2 2

To generate a medium-sized dataset with 3 blocks / 3 stacks:

    ./generate_all.sh 3 3

To generate a large dataset with 5 blocks / 3 stacks (>80k states=images),
running it on a single computer would take a lot of time.
If you have access to a compute cluster, you can distribute the workload
to the job scheduler.
You should customize the job submission command in `generate_all.sh` for your job scheduler.
Once you get done, run

    ./generate_all.sh 5 3 true

# Citation

``` bibtex
@article{asai2018blocksworld,
	author = {Asai, Masataro},
	journal = {arXiv preprint arXiv:1812.01818},
	title = {{Photo-Realistic Blocksworld Dataset}},
	year = {2018}
}
```

Relevant citation:

``` bibtex
@article{asai2018perminv,
	author = {Asai, Masataro},
	journal = {arXiv preprint arXiv:1812.01217},
	title = {{Set Cross Entropy: Likelihood-based Permutation Invariant Loss Function for Probability Distributions}},
	year = {2018}
}
```

