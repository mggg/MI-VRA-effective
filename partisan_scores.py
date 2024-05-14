import numpy as np

def s_efficiency_gap(partition, election, pos_party = "Democratic"):
    # S,V shares, should be Dem to match other EG
    total_seats = float(len(partition))
    seat_share = partition[election].seats(pos_party) / total_seats

    vote_share = partition[election].percent(pos_party)
    # S-2V+1/2
    s_eg = seat_share - 2*vote_share + 1/2
    
    return(s_eg)



def mean_disprop(partition, elections, pos_party = "Democratic"):
    # sum over elections of seat share - vote share
    return sum(partition[e].seats(pos_party) / float(len(partition)) - partition[e].percent(pos_party) for e in elections)

def lopsided_updater(partition, election_name, party1_name, pos_party):
    # pos party is the party for which a positive value of the score indicates favoring

    party_1_percents = np.array(partition[election_name].percents(party1_name))
    pos_party_percents = np.array(partition[election_name].percents(pos_party))
    total = party_1_percents + pos_party_percents
    # If any of the totals are not 1, then there are some missing votes
    # due to third party candidates or missing data, so we want to
    # scale each part in the partition to deal with just the two major parties
    if any(total != 1):
        party_1_percents = party_1_percents / total
        pos_party_percents = pos_party_percents / total

    return (
        party_1_percents[party_1_percents > 0.5].mean() if party_1_percents[party_1_percents > 0.5].size > 0 else 0
        - pos_party_percents[pos_party_percents > 0.5].mean() if pos_party_percents[pos_party_percents > 0.5].size > 0 else 0
    )
    