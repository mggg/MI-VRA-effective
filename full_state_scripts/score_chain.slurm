#!/bin/bash
#SBATCH --job-name="ScoreEnsemble-PlanAnalysis" # Job name
#SBATCH --time=02:00:00 # days-hh:mm:ss
#SBATCH --nodes=1 # how many computers do we need?
#SBATCH --ntasks-per-node=1 # how many cores per node do we need?
#SBATCH --mail-type=ALL
#SBATCH --mail-user=donnay.1@osu.edu

source ~/.bashrc  # need to set up the normal environment.
echo scoring

# cd into the correct directory
cd /cluster/tufts/mggg/cdonna01/MI_effective

# $state $map $n $county_weight $county_sub_weight $vra_type $theta $bvap $biden
if [ $6 == 0 ]
then
    echo ${1} ${2} ${3} ${4} ${5} ${7} ${8} ${9} ${10}
    python collect_scores.py ${1} ${2} ${3} ${4} ${5} ${7} ${8} ${9} ${10}
elif [ $6 == 1 ]
then
    echo ${1} ${2} ${3} ${4} ${5} ${7} ${8} ${9} ${10} --VRA_reject
    python collect_scores.py ${1} ${2} ${3} ${4} ${5} ${7} ${8} ${9} ${10} --VRA_reject
else
    echo ${1} ${2} ${3} ${4} ${5} ${7} ${8} ${9} ${10} --VRA_climb
    python collect_scores.py ${1} ${2} ${3} ${4} ${5} ${7} ${8} ${9} ${10} --VRA_climb
fi