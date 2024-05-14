#!/bin/bash

state="Michigan"
echo $state
n=100000
echo $n

#test
theta=100
bvap=.44
biden=.5

for stat in "avg_s_efficiency_gap" #"efficiency_gap" "s_efficiency_gap" "num_competitive_districts" "avg_efficiency_gap" "avg_s_efficiency_gap" "avg_mean_median" "avg_lopsided_margin" "mean_disprop" 
do
sbatch --mem=35G MI_scatter_restricted.sh house_1  0.0 .66 $theta $bvap $biden $stat
sbatch --mem=35G MI_scatter_restricted.sh house_2  0.0 .66 $theta $bvap $biden $stat
sbatch --mem=15G MI_scatter_restricted.sh senate  0.0 .66 $theta $bvap $biden $stat
done

