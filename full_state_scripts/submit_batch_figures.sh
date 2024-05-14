#!/bin/bash

# This script is meant to act as a sentinel to submit
# jobs to the slurm scheduler. The main idea is that the
# running script will be the one that calls the process
# that takes up the most time 



# ==============
# JOB PARAMETERS
# ==============

# This is the identifier that slurm will use to help
# keep track of the jobs. Please make sure that this
# does not exceed 80 characters.
job_name="MI_effective_figures_$(date '+%d-%m-%Y@%H:%M:%SET')"

# This controls how many jobs the scheduler will
# see submitted at the same time.
max_concurrent_jobs=500

# This is the name of the script that will be run
# to actually process all of the files and do the 
# you may need to modify the call to this script
# on line 167 or so
running_script_name="single_run_figures.sh"


# ==================
# RUNNING PARAMETERS
# ==================
log_dir="figure_logs"
state=Michigan
maps=("state_house" "state_senate" "congress")

# conditional!

# county_weights=.66 #(0 .33 .66 1)
# county_sub_weights=.66 #(0 .33 .66 1)
vra_types=(0 1 2)
bvaps=.44 #(.4 .44) #(.4 .44 .46 .5)
bidens=.5 #(.48 .5) #(.5 .53 .54 .55)
N=100000




# ===============================================================
# Ideally, you should not need to modify anything below this line
# However, you may need to modify the call on line 167
# ===============================================================

mkdir -p "${log_dir}"

job_ids=()
job_index=0

echo "========================================================"
echo "The job name is: $job_name"
echo "========================================================"

# This function will generate a label for the log and output file
generate_file_label() {
    local state="$1"
    local map="$2"
    local N="$3"
    local county_weight="$4"
    local county_sub_weight="$5"
    local vra_type="$6"
    local bvap="$7"
    local biden="$8"


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
        | tr ' ' '_'
    # The tr command replaces spaces with underscores so that
    # the file names are a bit nicer to read
}

# Indentation modified for readability

for map in "${maps[@]}"; do
if [ $map == "state_house" ]; then
    county_weights=.33 
    county_sub_weights=.33 
elif [ $map == "state_senate" ]; then
    county_weights=.33 
    county_sub_weights=.66 
else
    county_weights=.66 
    county_sub_weights=.66
fi

for county_weight in "${county_weights[@]}"; do
for county_sub_weight in "${county_sub_weights[@]}"; do
for vra_type in "${vra_types[@]}"; do
for bvap in "${bvaps[@]}"; do
for biden in "${bidens[@]}"; do

    file_label=$(generate_file_label \
        "$state" \
        "$map" \
        "$N" \
        "$county_weight" \
        "$county_sub_weight" \
        "$vra_type" \
        "$bvap" \
        "$biden" \
    )
    
    log_file="${log_dir}/${file_label}.log"

    # Waits for the current number of running jobs to be
    # less than the maximum number of concurrent jobs
    while [[ ${#job_ids[@]} -ge $max_concurrent_jobs ]] ; do
        # Check once per minute if there are any open slots
        sleep 60
        # We check for the job name, and make sure that squeue prints
        # the full job name up to 100 characters
        job_count=$(squeue --name=$job_name --Format=name:100 | grep $job_name | wc -l)
        if [[ $job_count -lt $max_concurrent_jobs ]]; then
            break
        fi
    done

    # Some logging for the 
    for job_id in "${job_ids[@]}"; do
        if squeue -j $job_id 2>/dev/null | grep -q $job_id; then
            continue
        else
            job_ids=(${job_ids[@]/$job_id})
            echo "Job $job_id has finished or exited."
        fi
    done

    # This output will be of the form "Submitted batch job 123456"
    job_output=$(sbatch --job-name=${job_name} \
        --output="${log_file}" \
        --error="${log_file}" \
        $running_script_name \
            "$state" \
            "$map" \
            "$N" \
            "$county_weight" \
            "$county_sub_weight" \
            "$vra_type" \
            "$bvap" \
            "$biden" \
            "$log_file"\
    )
    # Extract the job id from the output. The awk command
    # will print the last column of the output which is
    # the job id in our case
    # 
    # Submitted batch job 123456
    #                     ^^^^^^
    job_id=$(echo "$job_output" | awk '{print $NF}')
    echo "Job output: $job_output"
    # Now we add the job id to the list of running jobs
    job_ids+=($job_id)
    # Increment the job index. Bash allows for sparse
    # arrays, so we don't need to worry about any modular arithmetic
    # nonsense
    job_index=$((job_index + 1))
done
done
done
done
done
done


# This is just a helpful logging line to let us know that all jobs have been submitted
# and to tell us what is still left to be done
printf "No more jobs need to be submitted. The queue is\n%s\n" "$(squeue --name=$job_name)"
# Check once per minute until the job queue is empty
while [[ ${#job_ids[@]} -gt 0 ]]; do
    sleep 60
    for job_id in "${job_ids[@]}"; do
        if squeue -j $job_id 2>/dev/null | grep -q $job_id; then
            continue
        else
            job_ids=(${job_ids[@]/$job_id})
            echo "Job $job_id has finished or exited."
        fi
    done

    job_ids=("${job_ids[@]}")
done

echo "All jobs have finished."