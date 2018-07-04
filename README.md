
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
