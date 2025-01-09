# Useful scripts

## `get_calibration_data.py`

This is an example of how to get the figures of merit or quality metrics set from the API using `iqm_client`. Using the `get_calibration_data` function, you can print the current calibration set data or query past calibration sets if you have a given calibration_setid. The function also allows you to export these results into a json file.

## `int_job.sh`

Simple script to clear the terminal and run an interactive job. Run with `bash int_job.sh 'qb_flip_qiskit.py --backend helmi'` or edit it for your own usage! Note that you need to replace the 'project_xxx' with your LUMI project id.


## `batch_script.sh`

Example batch script for submitting jobs to the `q_fiqci` partition. Run with `sbatch batch_script 'qb_flip_qiskit.py --backend helmi'` or edit it for your own usage! Note that you need to replace the 'project_xxx' with your LUMI project id.
