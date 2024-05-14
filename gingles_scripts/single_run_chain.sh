#!/bin/bash
#SBATCH --time=02-01:00:00 # days-hh:mm:ss
#SBATCH --nodes=1 # how many computers do we need?
#SBATCH --ntasks-per-node=1 # how many cores per node do we need?
#SBATCH --mem=2000 # how many MB of memory do we need (4GB here)
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=christopherdonnay@gmail.com

source ~/.bashrc  # need to set up the normal environment.

# cd into the correct directory
cd /cluster/tufts/mggg/cdonna01/MI_effective
log_file=$7

plan_type=${1} 
steps=${2} 
county_weight=${3} 
county_sub_weight=${4}
tilt_prob=${5} 
burst_length=${6}



echo ${1} ${2} ${3} ${4} ${5} ${6} 
echo ${7} 
python run_ensemble_gingles.py $plan_type $steps $county_weight $county_sub_weight $tilt_prob $burst_length
