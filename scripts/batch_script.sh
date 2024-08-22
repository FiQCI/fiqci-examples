#!/bin/bash -l

#SBATCH --job-name=helmijob   # Job name
#SBATCH --output=helmijob.o%j # Name of stdout output file
#SBATCH --error=helmijob.e%j  # Name of stderr error file
#SBATCH --partition=q_fiqci   # Partition (queue) name
#SBATCH --ntasks=1            # One task (process)
#SBATCH --cpus-per-task=1     # Number of cores (threads)
#SBATCH --time=00:15:00       # Run time (hh:mm:ss)
#SBATCH --account=project_xxx # Project for billing
#SBATCH --mem-per-cpu=1G      # Memory per CPU

module use /appl/local/quantum/modulefiles
module load helmi_qiskit  # Load the module to use qiskit on Helmi

# module load helmi_cirq    # Load the module to use cirq on Helmi

# Save the job ID to a file for later reference
echo $SLURM_JOB_ID >> job_id.txt

python -u $1
