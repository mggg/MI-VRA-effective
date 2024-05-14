#!/bin/bash
#SBATCH --time=01-01:00:00 # days-hh:mm:ss
#SBATCH --nodes=1 # how many computers do we need?
#SBATCH --ntasks-per-node=1 # how many cores per node do we need?
#SBATCH --mem=2000 # how many MB of memory do we need (4GB here)
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=christopherdonnay@gmail.com

source ~/.bashrc  # need to set up the normal environment.

# cd into the correct directory
cd /cluster/tufts/mggg/cdonna01/MI_effective
log_file=$3

plan_type=${1} 
file=${2} 



echo ${1} ${2}
python score_gingles.py $plan_type $file
