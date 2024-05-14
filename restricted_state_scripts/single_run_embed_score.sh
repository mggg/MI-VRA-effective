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
log_file=$9


# $state $map $n $county_weight $county_sub_weight $vra_type $bvap $biden $logfile
if [ $6 == 0 ]
then
    echo ${1} ${2} ${3} ${4} ${5} ${7} ${8} 
    python collect_scores_embed_partial.py ${2} ${3} ${4} ${5} 2 ${7} ${8} 
elif [ $6 == 1 ]
then
    echo ${1} ${2} ${3} ${4} ${5} ${7} ${8}  --VRA_reject 
    python collect_scores_embed_partial.py ${2} ${3} ${4} ${5} 2 ${7} ${8}  --VRA_reject
else
    echo ${1} ${2} ${3} ${4} ${5} ${7} ${8}  --VRA_climb
    python collect_scores_embed_partial.py ${2} ${3} ${4} ${5} 100 ${7} ${8}  --VRA_climb
    
fi

sacct -j $SLURM_JOB_ID --format=JobID,JobName,Partition,State,ExitCode,Start,End,Elapsed,NCPUS,NNodes,NodeList,ReqMem,MaxRSS,AllocCPUS,Timelimit,TotalCPU >> "$log_file" 2>> "$log_file"