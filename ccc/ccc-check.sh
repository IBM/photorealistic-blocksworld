#!/bin/bash


parallel "ssh {} \"echo '------' ; hostname ; $(readlink -ef $1)\"" ::: $(echo dccxc{001..183} dccxc{201..280} | tr ' ' '\n' | sort -R | head)
