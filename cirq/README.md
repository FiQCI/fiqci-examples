# Helmi Cirq Examples

Examples made through Cirq which are optimised for use on Helmi. These examples were made with the aim to show how simple quantum jobs can be run on Helmi and to also demonstate the differences in results between the simulator and the real quantum computer. Therefore each example has the option to run with a simulator or with the Quantum Computer, Helmi. Running jobs on Helmi requires submitting of jobs through SLURM with the `--partition q_fiqci` option.

## Example list

| Example                            | Code              | Quick run                                |
|------------------------------------|-------------------|------------------------------------------|
| [Qubit Flipping]( #qubit-flipping) | `qb_flip.py` | `python qb_flip.py --backend helmi` |
| [GHZ state]( #ghz-state)           | `ghz.py`          | `python ghz.py --backend helmi`          |

All examples have command line arguments which can be viewed with the `-h` or `--help` option. You can run the scripts with the `-h` option in the login node. Using this also prints some example usage for each example. Each example also has the verbose option built in, add the `-v` or `--verbose` command line argument.

## Running on LUMI


To run these examples on LUMI you will need to:

- `module use /appl/local/quantum/modulefiles`
- `module load helmi_cirq`

Then jobs can be run through the batch queueing system, SLURM. For accessing Helmi (with `--backend helmi`) you will need to submit jobs to the `q_fiqci` slurm partition. Here are some example job submission scripts. Bash script versions can be found in the `scripts` directory.

For interactive usage:

```bash
srun --account project_xxx -t 00:15:00 -c 1 -n 1 --partition q_fiqci python -u qb_flip.py --backend helmi
```

This will print the output to the terminal. The `-u` option enables constant updating of the output through python.


As a batch script:


```bash
#!/bin/bash -l

#SBATCH --job-name=helmijob   # Job name
#SBATCH --output=helmijob.o%j # Name of stdout output file
#SBATCH --error=helmijob.e%j  # Name of stderr error file
#SBATCH --partition=q_fiqci   # Partition (queue) name
#SBATCH --ntasks=1              # One task (process)
#SBATCH --cpus-per-task=1     # Number of cores (threads)
#SBATCH --time=00:15:00         # Run time (hh:mm:ss)
#SBATCH --account=project_xxx  # Project for billing

module use /appl/local/quantum/modulefiles
module load helmi_cirq

python -u qb_flip.py --backend helmi
```

The output will then be redirected to filenames in your submission directory called `helmijob.o` and `helmijob.e`.


### Qubit Flipping

The Qubit flipping example, `qb_flip.py`, demonstrates simple qubit flipping. The example first flips the qubit state of each qubit (QB1, QB2,...) individually and reports the success rate which is how many out of the 10,000 counts are expected to be in the right state. The program then flips all the qubits at once in a 5 qubit circuit and reports the total success rate.


## Additional examples

Additional example can be found on the [Cirq on IQM](https://iqm-finland.github.io/cirq-on-iqm/user_guide.html) Website.
