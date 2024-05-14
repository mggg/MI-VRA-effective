#!/bin/bash
#SBATCH --job-name="MI figures" # Job name
#SBATCH --time=00-00:45:00 # days-hh:mm:ss
#SBATCH --nodes=1 # how many computers do we need?
#SBATCH --mem=44000 #(44g)
#SBATCH --ntasks-per-node=1 # how many cores per node do we need?
#SBATCH --mail-type=ALL
#SBATCH --mail-user=donnay.1@osu.edu

source ~/.bashrc  # need to set up the normal environment.
export PYTHONHASHSEED=0

# cd into the correct directory
cd /cluster/tufts/mggg/cdonna01/MI_effective

echo "making ensemble stats table"
python ensemble_stats_table.py