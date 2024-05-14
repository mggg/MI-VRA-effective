#!/bin/bash
#!/bin/bash

state="Michigan"
echo $state
n=100000
echo $n

biden=.5
bvap=.44
theta=2.0
# 0 neutral, 1 reject, 2 climb
# vra_type=2
# theta=2

# test
# # sbatch --mem=4G MI_figures.sh  congress  "vra_neutral" .33 .66 $theta $bvap $biden
# for theta in 10 50 100
# do
# for biden in .5 .53 .54 .55
# do
# for bvap in .4 .44 .46 .5
# do
sbatch --mem=18G MI_figures.sh  congress  "vra_neutral" .66 .66  $theta $bvap $biden
sbatch --mem=18G MI_figures.sh  state_senate  "vra_neutral" .33 .66  $theta $bvap $biden
sbatch --mem=18G MI_figures.sh  state_house  "vra_neutral" .33 .33  $theta $bvap $biden
# done
# done

# # climb
# vra_type=2
# theta=100
# sbatch --mem=18G MI_figures.sh  congress "vra_climb" .66 .66  $theta $bvap $biden
# sbatch --mem=18G MI_figures.sh  state_senate "vra_climb" .33 .66  $theta $bvap $biden
# sbatch --mem=18G MI_figures.sh  state_house "vra_climb" .33 .33  $theta $bvap $biden


# vra_type=1
# theta=2
# sbatch --mem=18G MI_figures.sh congress "vra_reject" .66 .66  $theta $bvap $biden
# sbatch --mem=18G MI_figures.sh  state_senate "vra_reject" .33 .66  $theta $bvap $biden
# sbatch --mem=18G MI_figures.sh state_house "vra_reject" .33 .33  $theta $bvap $biden

# state="Michigan"
# echo $state

# for map in  "congress" #"state_senate" "state_house" #"state_senate" #
# do
#     for county_weight in 0 .33 .66 1
#     do
#         for county_sub_weight in 0 .33 .66 1
#         do
#             for bvap in .4 .44 .46 .5
#             do
#                 for biden in .5 .53 .54 .55
#                 do
#                     for vra_type in "vra_neutral" "vra_reject" "vra_climb"
#                     do

#                         if [ ${vra_type} == "vra_climb" ]
#                         then
#                             for theta in 10 50 100
#                             do
#                                 sbatch MI_figures.sh $map $vra_type $county_weight $county_sub_weight $theta $bvap $biden
#                             done

#                         else
#                             sbatch MI_figures.sh $map $vra_type $county_weight $county_sub_weight 2 $bvap $biden
#                         fi
#     done
# done
# done
# done
# done
# done
