#!/bin/bash

# Define the parameters
tsize="4k 1m 2m"
bsize="200k 20m 2g"
output_path="/hdd-share/ior_out/"


export DARSHAN_ENABLE_NONMPI=1
spack load ior@3.3.0

# Loop through each combination of parameters
for t in $tsize; do
    for b in $bsize; do
            echo "Running program with -t = $t -b = $b"
            # for HPCA004
            LD_PRELOAD=/home/luser/Repos/spack/opt/spack/linux-almalinux9-ivybridge/gcc-11.4.1/darshan-runtime-3.4.4-ykayvipyjq7hnrzq7qeqs5ekpn6nga4t/lib/libdarshan.so ior -a POSIX -b "$b" -t "$t" -e -C -o "$output_path"
            # for HPCA003
            # LD_PRELOAD=/home/luser/Repos/spack/opt/spack/linux-almalinux9-ivybridge/gcc-11.4.1/darshan-runtime-3.4.4-3elp6ce775ewdazycqrxmkbyi6em2x76/lib/libdarshan.so ior -a POSIX -b "$b" -t "$t" -e -C -o "$output_path"
    done
done