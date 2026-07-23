#!/bin/bash

#SBATCH --job-name=quantumjob   # Job name
#SBATCH --account=project_<id>  # Project for billing (slurm_job_account)
#SBATCH --partition=small   # Partition (queue) name
#SBATCH --ntasks=1              # One task (process)
#SBATCH --mem-per-cpu=2G       # memory allocation
#SBATCH --cpus-per-task=1     # Number of cores (threads)
#SBATCH --time=00:15:00         # Run time (hh:mm:ss)

module use /appl/local/quantum/modulefiles
module load fiqci-vtt-qiskit

# or for cirq, use the following instead of the above two lines
# module use /appl/local/quantum/modulefiles
# module load fiqci-vtt-cirq

export DEVICES=("Q50") # available devices: Q50, radiance20
source $RUN_SETUP

python -u $1