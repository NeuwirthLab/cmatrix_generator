#!/bin/bash

# Define the parameters
dims="10 100 1000 10000"
input_path="/Users/zhaobinzhu/research-stuff/repos/cmatrix-generator/test.mtx"
output_path="/Users/zhaobinzhu/research-stuff/repos/cmatrix-generator/test.mtx"

export DARSHAN_ENABLE_NONMPI=1
# Loop through each combination of parameters
for d in $dims; do
  echo "Running program with --rows=$d --cols=$d"
  LD_PRELOAD=/path_to/lib/libdarshan.so /cmatrix_generator -i $input_path -o $output_path -cols $d -r $d
  # ssh to remote machine and execute the consumer program
  # ssh -t user@remote_machine "LD_PRELOAD=/path_to_remote/lib/libdarshan.so /matrix_operations -i $output_path -o $output_path"
  echo "Done"
done



