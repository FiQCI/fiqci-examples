#!/bin/bash

# Usage:
# bash int_job.sh <your_python_script.py> --backend Q5 Q50 --project project_xxx

clear
module use /appl/local/quantum/modulefiles
module --ignore_cache load "fiqci-vtt-qiskit"

# module load fiqci-vtt-cirq    # Load the module to use cirq on Helmi

# Parse arguments
BACKENDS=()
SCRIPT=""
SCRIPT_ARGS=()
PROJECT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --backend)
            shift
            while [[ $# -gt 0 && ! "$1" =~ ^-- ]]; do
                BACKENDS+=("$1")
                shift
            done
            ;;
        --project)
            shift
            if [[ $# -gt 0 ]]; then
                PROJECT="$1"
                shift
            fi
            ;;
        *)
            if [[ -z "$SCRIPT" ]]; then
                SCRIPT="$1"
            else
                SCRIPT_ARGS+=("$1")
            fi
            shift
            ;;
    esac
done

# Export devices
export DEVICES=("${BACKENDS[@]}")

if [[ ${#BACKENDS[@]} -gt 0 ]]; then
    SCRIPT_ARGS+=(--backend "${BACKENDS[@]}")
fi

# Launch job
srun --account $PROJECT \
     --time=00:15:00 \
     --cpus-per-task=1 \
     --ntasks=1 \
     --partition=q_fiqci \
     bash -c "source $RUN_SETUP && python -u $SCRIPT ${SCRIPT_ARGS[*]}"
