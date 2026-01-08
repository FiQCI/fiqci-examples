#!/bin/bash -l

#SBATCH --job-name=qcjob   # Job name
#SBATCH --output=out.txt # Name of stdout output file
#SBATCH --error=err.txt  # Name of stderr error file
#SBATCH --partition=q_fiqci   # Partition (queue) name
#SBATCH --ntasks=1            # One task (process)
#SBATCH --cpus-per-task=1     # Number of cores (threads)
#SBATCH --time=00:15:00       # Run time (hh:mm:ss)
#SBATCH --account=project_xxxxxxx # Project for billing
#SBATCH --mem-per-cpu=1G      # Memory per CPU

module use /appl/local/quantum/modulefiles
module load fiqci-vtt-qiskit  # Load the module to use qiskit on Helmi

# module load fiqci-vtt-cirq    # Load the module to use cirq on Helmi

export DEVICES=("Q5") # for Q50 use export DEVICES=("Q50")
                      # for both Q5 and Q50 use export DEVICES=("Q5" "Q50")

source $RUN_SETUP

python -u $1 # Usage: sbatch batch_script.sh <your_python_script.py>
