#!/bin/bash
#SBATCH --time=02-01:00:00 # days-hh:mm:ss
#SBATCH --nodes=1 # how many computers do we need?
#SBATCH --ntasks-per-node=1 # how many cores per node do we need?
#SBATCH --mem=2000 # how many MB of memory do we need (4GB here)
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=christopherdonnay@gmail.com

source ~/.bashrc  # need to set up the normal environment.


state=${1} 
map=${2} 
n=${3} 
county_weight=${4} 
county_sub_weight=${5} 
bvap=${6} 
biden=${7} 
logfile=${8}
theta=${9}
vra_type=2

# cd into the correct directory
cd /cluster/tufts/mggg/cdonna01/MI_effective

generate_file_label() {
    local state="$1"
    local map="$2"
    local N="$3"
    local county_weight="$4"
    local county_sub_weight="$5"
    local vra_type="$6"
    local bvap="$7"
    local biden="$8"
    local theta="$9"


    # Use string substistution to replace spaces with dashes
    # This will make the files nicer to work with in the command line
    echo "${state// /-}"\
        "map_${map// /-}"\
        "N_${N// /-}"\
        "county_weight_${county_weight// /-}"\
        "county_sub_weight_${county_sub_weight// /-}"\
        "vra_type${vra_type// /-}"\
        "bvap_${bvap// /-}"\
        "biden_${biden// /-}"\
        "theta_${theta// /-}"\
        | tr ' ' '_'
    # The tr command replaces spaces with underscores so that
    # the file names are a bit nicer to read
}

file_label=$(generate_file_label \
        "$state" \
        "$map" \
        "$n" \
        "$county_weight" \
        "$county_sub_weight" \
        "$vra_type" \
        "$bvap" \
        "$biden" \
        "$theta" \
    )
log_file="restricted_state_scripts/logs/${file_label}.log"
python run_restricted_ensemble.py $state $map $n $county_weight $county_sub_weight $theta $bvap $biden  --VRA_climb
sacct -j $SLURM_JOB_ID --format=JobID,JobName,Partition,State,ExitCode,Start,End,Elapsed,NCPUS,NNodes,NodeList,ReqMem,MaxRSS,AllocCPUS,Timelimit,TotalCPU >> "$log_file" 2>> "$log_file"