#!/bin/bash
n=100000
bvap=0.44
biden=0.5


for stat in "num_competitive_districts" #"avg_efficiency_gap" "avg_s_efficiency_gap" "avg_mean_median" "avg_lopsided_margin" "mean_disprop" "num_d_seats_pres_16"
do
state="Michigan"
echo $state
sbatch --mem=35G MI_num_effective_figs.sh $state state_house 0.33 0.33 $bvap $biden $stat
sbatch --mem=35G MI_num_effective_figs.sh $state state_senate  0.33 0.66 $bvap $biden $stat
sbatch --mem=35G MI_num_effective_figs.sh $state congress  0.66 0.66  $bvap $biden $stat

state="Michigan_embed"
echo $state
sbatch --mem=40G MI_num_effective_figs.sh $state house_1 0.0 0.66 $bvap $biden $stat
sbatch --mem=40G MI_num_effective_figs.sh $state house_2  0.0 0.66 $bvap $biden $stat
sbatch --mem=35G MI_num_effective_figs.sh $state senate  0.0 0.66  $bvap $biden $stat


done
