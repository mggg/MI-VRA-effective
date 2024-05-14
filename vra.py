import numpy as np


def is_effective(district, partition, bvap_thresh, biden_thresh):
    # compute BVAP and Biden total

    # make sure bvap percentage is at least .43 and biden is at least .53
    if partition["PRES20"].percent("Democratic", district) >= biden_thresh and partition["BVAP"][district]/partition["VAP"][district] >= bvap_thresh:
        return True
    
    return False

def num_effective_districts(partition, bvap_thresh, biden_thresh):
    # takes in a map, returns the number of effective districts per some definition

    return sum(is_effective(district, partition, bvap_thresh, biden_thresh) for district in partition.parts)

def vra_metropolis(proposed_partition, theta = 2, bvap_thresh=.4, biden_thresh=.5):
    # returns true or false based on MH rule for number of effective districts
    # delta is at most 1, so theta can be pretty big

    proposed_score = num_effective_districts(proposed_partition, bvap_thresh, biden_thresh)
    current_score = num_effective_districts(proposed_partition.parent, bvap_thresh, biden_thresh)

    if proposed_score >= current_score:
        return True
    
    else:
        u = np.random.uniform()

        if u < pow(theta, -(current_score-proposed_score)):
            return True
        else:
            return False

    


