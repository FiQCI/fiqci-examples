#!/bin/bash

# Launch this script as
# > bash int_job.sh 'qb_flip_qiskit.py --backend helmi'

clear
srun --account project_xxx -t 00:15:00 -c 1 -n 1 --partition q_fiqci python -u $1
