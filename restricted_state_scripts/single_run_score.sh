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
    # feed in value for theta 
    python collect_restricted_scores.py ${1} ${2} ${3} ${4} ${5} 2 ${7} ${8} 
elif [ $6 == 1 ]
then
    echo ${1} ${2} ${3} ${4} ${5} ${7} ${8}  --VRA_reject 
    # feed in value for theta 
    python collect_restricted_scores.py ${1} ${2} ${3} ${4} ${5} 2 ${7} ${8}  --VRA_reject
else
    #if vra_climb, submit 3 batch jobs for values of theta
    echo ${1} ${2} ${3} ${4} ${5} ${7} ${8}  --VRA_climb
    cd /cluster/tufts/mggg/cdonna01/MI_effective/restricted_state_scripts
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
        "$1" \
        "$2" \
        "$3" \
        "$4" \
        "$5" \
        "$6" \
        "$7" \
        "$8" \
        "10" \
    )
    log_file="score_logs/${file_label}.log"
    sbatch --job-name="vra climb" --output="${log_file}" \
        --error="${log_file}" vra_climb_score.sh ${1} ${2} ${3} ${4} ${5} ${7} ${8} $log_file 10

    file_label=$(generate_file_label \
        "$1" \
        "$2" \
        "$3" \
        "$4" \
        "$5" \
        "$6" \
        "$7" \
        "$8" \
        "50" \
    )
    log_file="score_logs/${file_label}.log"
    sbatch --job-name="vra climb" --output="${log_file}" \
        --error="${log_file}" vra_climb_score.sh ${1} ${2} ${3} ${4} ${5} ${7} ${8} $log_file 50

    file_label=$(generate_file_label \
        "$1" \
        "$2" \
        "$3" \
        "$4" \
        "$5" \
        "$6" \
        "$7" \
        "$8" \
        "100" \
    )
    log_file="score_logs/${file_label}.log"
    sbatch --job-name="vra climb" --output="${log_file}" \
        --error="${log_file}" vra_climb_score.sh ${1} ${2} ${3} ${4} ${5} ${7} ${8} $log_file 100
fi

sacct -j $SLURM_JOB_ID --format=JobID,JobName,Partition,State,ExitCode,Start,End,Elapsed,NCPUS,NNodes,NodeList,ReqMem,MaxRSS,AllocCPUS,Timelimit,TotalCPU >> "$log_file" 2>> "$log_file"