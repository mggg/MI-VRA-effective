#!/bin/bash

# This script is just meant to make it easier to submit
# the sentinel script to the slurm scheduler.

sentinel_name="MI_effective_sentinel_score_run_$(date '+%d-%m-%Y@%H:%M:%SET')"

sentinel_script="submit_batch_score.sh"

sbatch --nodes=1\
    --cpus-per-task=1\
    --ntasks-per-node=1\
    --mem=1G\
    --time=0-12:00:00\
    --job-name="$sentinel_name"\
    --output="$sentinel_name.out"\
    --error="$sentinel_name.out"\
    $sentinel_script

# DON'T FORGET TO GO THROUGH THE CALLED SCRIPTS AND MAKE SURE
# THAT THE PARAMETERS ARE SET CORRECTLY INCLUDING THE SBATCH 
# PARAMETERS IN THE SCRIPT CALLED BY THE SENTINEL