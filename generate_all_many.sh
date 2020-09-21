#!/bin/bash

# generate blocks-3-3 with 100 different random colors and shapes

parallel -j 1 ./generate_all.sh 3 true 200 true /{} ::: {1..100}
