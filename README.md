
# CLEVR-blocksworld

This is a repository modified from the [CLEVR dataset](https://github.com/facebookresearch/clevr-dataset-gen)
for generating realistic visualizations of [blocksworld](https://en.wikipedia.org/wiki/Blocks_world).

Setup:

```
sudo apt-get install blender
echo $PWD >> ~/.local/lib/python3.5/site-packages/clevr.pth
```

Example: `./test.sh`

For the original readme, see [README-clevr.md](README-clevr.md) .

Note: I changed all keyword options from using underscores to using hyphens (e.g. `--use_gpu` -> `--use-gpu`) 

to use `extract_region.py`, you also need `imageio`. run `pip3 install --user imageio`

Example for extract_regions_binary.py:

./extract_regions_binary.py --maxobj 7 --out blocksworld.npz clevr_blocksworld


to generate the full datasets:

./generate_all.sh 2 2
./generate_all.sh 3 3
./generate_all.sh 5 3 true
