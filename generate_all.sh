#!/bin/bash

if [ -z "$@" ]
then

    cat <<EOF >&2


    Usage: generate_all.sh [objs] [num_images] [num_jobs] [gpu] [suffix]
    
      objs:   specity the number of objects, default = 2
    
      num_images:  The number of images to be rendered in total.
    
      num_jobs: how many jobs to use (default: 1). When the number is larger than 1, it switches to the distributed mode.
    
      gpu:  if true, use the gpu. default : true.
    
      suffix:  arbitrary string to be attached to the name of the output directory.


    Generate scenes randomly and render them.
    It reads an environment variable $SUBMIT as a job submission command template.
    It defaults to jbsub, which is a close-sourced script available in a particular compute cluster of the author.
    
    Use it like this: SUBMIT="qsub -V -b n -cwd" ./generate_all.sh 3 30000 50
    
EOF
    exit 1
fi

export objs=${1:-3}         ; shift 1
export num_images=${1:-200} ; shift 1
export num_jobs=${1:-1}     ; shift 1
export gpu=${1:-true}       ; shift 1
export suffix=$1            ; shift 1

if [ $num_jobs -gt 1 ]
then
    export distributed=true
else
    export distributed=false
fi
export dir="monoblocks-$objs$suffix"
export proj=render-$dir
export use_gpu=""
if $gpu
then
    export use_gpu="--use-gpu 1"
fi
  

SUBMIT=${SUBMIT:-"jbsub -mem 4g -cores 1+1 -queue x86_6h -proj $proj -require k80"}

job (){
    output_dir=$1
    start_idx=$2
    num_images=$3
    blenderdir=$(ls -d blender-2.*/ | tail -n 1)
    $blenderdir/blender -noaudio --background --python render_images.py -- \
                        --properties-json data/mono-properties.json \
                        --allow-duplicates \
                        --render-num-samples 150 \
                        --width 150              \
                        --height 100             \
                        --num-objects $objs      \
                        $use_gpu                 \
                        --output-dir $output_dir \
                        --start-idx $start_idx   \
                        --num-images $num_images
    ./extract_all_regions_binary.py  --out $output_dir-objs.npz --resize 16 16 $output_dir
    ./extract_all_regions_binary.py  --out $output_dir-bgnd.npz --resize 16 16 --include-background $output_dir
    ./extract_all_regions_binary.py  --out $output_dir-flat.npz --resize 40 60 --include-background --exclude-objects $output_dir
    ./extract_all_regions_binary.py  --out $output_dir-high.npz --resize 80 120 --include-background --exclude-objects $output_dir
}

export -f job
# for parallel to recognize the shell function
export SHELL=/bin/bash

if $distributed
then
    num_images_per_job=$((num_images/num_jobs))
    parallel "$SUBMIT job $dir/{} {} $num_images_per_job" ::: $(seq 0 $num_images_per_job $((num_images-num_images_per_job)))
    echo "Run the following command when all jobs have finished:"
    echo "./merge-npz.py --out $dir-objs.npz $dir/*-objs.npz"
    echo "./merge-npz.py --out $dir-bgnd.npz $dir/*-bgnd.npz"
    echo "./merge-npz.py --out $dir-flat.npz $dir/*-flat.npz"
else
    job $dir 0 $num_images
fi
