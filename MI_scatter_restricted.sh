#!/bin/bash
#SBATCH --job-name="MI figures" # Job name
#SBATCH --time=00-00:40:00 # days-hh:mm:ss
#SBATCH --nodes=1 # how many computers do we need?
#SBATCH --ntasks-per-node=1 # how many cores per node do we need?
#SBATCH --mail-type=ALL
#SBATCH --mail-user=donnay.1@osu.edu

source ~/.bashrc  # need to set up the normal environment.
export PYTHONHASHSEED=0

# cd into the correct directory
cd /cluster/tufts/mggg/cdonna01/MI_effective

echo scatter plotting
echo $1 $2 $3 $4 $5 $6 $7

if [ $7 == "efficiency_gap" ] || [ $7 == "s_efficiency_gap" ]
then # use all three indices
python MI_scatterplots_restricted.py $1 $2 $3 $4 $5 $6 $7 0
python MI_scatterplots_restricted.py $1 $2 $3 $4 $5 $6 $7 1
python MI_scatterplots_restricted.py $1 $2 $3 $4 $5 $6 $7 3
else
python MI_scatterplots_restricted.py $1 $2 $3 $4 $5 $6 $7 47
fi