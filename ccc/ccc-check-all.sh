#!/bin/bash


parallel "ssh -o \"ConnectTimeout=3\" {} \"echo '------' ; hostname ; $(readlink -ef $1)\"" ::: $(echo dccxc{001..180} dccxc{201..280} | tr ' ' '\n')
