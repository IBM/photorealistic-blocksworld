
# CLEVR-blocksworld

This is a repository modified from the [CLEVR dataset](https://github.com/facebookresearch/clevr-dataset-gen)
for generating realistic visualizations of [blocksworld](https://en.wikipedia.org/wiki/Blocks_world).

Setup:

```
sudo apt-get install blender parallel
pip3 install --user imageio scikit-image
echo $PWD >> ~/.local/lib/python3.5/site-packages/clevr.pth
```

Example: `./test.sh`

For the original readme, see [README-clevr.md](README-clevr.md) .

Note: I changed all keyword options from using underscores to using hyphens (e.g. `--use_gpu` -> `--use-gpu`).

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

