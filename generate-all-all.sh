#!/bin/bash


parallel ./generate_all.sh {} 30000 50 ::: {3..6}

list-proj
