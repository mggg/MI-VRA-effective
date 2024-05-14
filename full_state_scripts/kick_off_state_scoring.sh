#!/bin/bash

state="Michigan"
echo $state
n=100000
echo $n

for map in "state_house" "state_senate" "congress"
do
    if [ $map == "state_house" ]
    then
        county_weights=.33 #(0 .33 .66 1)
        county_sub_weights=.33 #(0 .33 .66 1)
    elif [ $map == "state_senate" ]
    then
        county_weights=.33 #(0 .33 .66 1)
        county_sub_weights=.66 #(0 .33 .66 1)
    else
        county_weights=.66 #(0 .33 .66 1)
        county_sub_weights=.66
    fi
    for county_weight in "${county_weights[@]}" 
    do
        for county_sub_weight in "${county_sub_weights[@]}"
        do
            for vra_type in 0 1 2
            do
                for bvap in .4 .44 #.46 .5
                do
                    for biden in .48 .5 #.53 .54 .55
                    do 
                        # for gingle in "" #"gingles" #("" "gingles")
                        # do

                        # vra climb
                        if [ $vra_type == 2 ]
                        then
                            for theta in 10 50 100
                            do  
                                sbatch score_chain.slurm $state $map $n $county_weight $county_sub_weight $vra_type $theta $bvap $biden #$gingle
                            done
                        
                        else
                            # if [ $gingle == "gingles" ]
                            # then
                            # sbatch score_chain.slurm $state $map $n $county_weight $county_sub_weight $vra_type 100 $bvap $biden $gingle
                            # sbatch score_chain.slurm $state $map $n $county_weight $county_sub_weight $vra_type 500 $bvap $biden $gingle
                            # sbatch score_chain.slurm $state $map $n $county_weight $county_sub_weight $vra_type 1000 $bvap $biden $gingle
                            # else    
                            sbatch score_chain.slurm $state $map $n $county_weight $county_sub_weight $vra_type 2 $bvap $biden #$gingle
                            # fi
                        
                        fi

    done
done
done
done
done
done
# done 