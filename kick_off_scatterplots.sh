#!/bin/bash

state="Michigan"
echo $state
n=100000
echo $n

#test
theta=100
bvap=.44
biden=.5

# for stat in "avg_efficiency_gap"
for stat in "avg_s_efficiency_gap" #"num_competitive_districts" "avg_efficiency_gap" "efficiency_gap" "avg_s_efficiency_gap" "s_efficiency_gap" "avg_mean_median" "avg_lopsided_margin" "mean_disprop" 
do
sbatch --mem=8G MI_scatter.sh congress  .66 .66 $theta $bvap $biden $stat
sbatch --mem=20G MI_scatter.sh state_senate  .33 .66 $theta $bvap $biden $stat
sbatch --mem=40G MI_scatter.sh state_house  .33 .33 $theta $bvap $biden $stat
done


