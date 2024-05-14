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
log_file=$8

plan_type=${1} 
steps=${2} 
county_weight=${3} 
county_sub_weight=${4}
hot=${5} 
cold=${6}
beta_magnitude=${7}



echo ${1} ${2} ${3} ${4} ${5} ${6} ${7} 
echo ${8} 
python run_ensemble_anneal.py $plan_type $steps $county_weight $county_sub_weight $hot $cold $beta_magnitude
