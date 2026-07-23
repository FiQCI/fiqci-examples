#!/bin/bash

# Launch this script as
# > bash int_job.sh 'qb_flip_qiskit.py'

clear

module use /appl/local/quantum/modulefiles
module --ignore_cache load "fiqci-vtt-qiskit" # or for cirq use fiqci-vtt-cirq instead of fiqci-vtt-qiskit
export DEVICES=("Q50") # available devices: Q50, radiance20
srun --account project_xxx -t 00:15:00 -c 1 -n 1 --partition q_fiqci bash -c "source $RUN_SETUP && python -u $1"