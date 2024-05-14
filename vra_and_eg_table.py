import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import gzip 

# make smaller for faster runs, but not getting full ensemble
TESTING_TRUNCATOR = 100000

biden_thresh  = .48
bvap_thresh = .44


map_type_relabeling = {"state_house": "HD", "state_senate": "SD", "house_1": "HD 1", "house_2": "HD 2", "senate": "SD 1", "congress": "CD"}
map_name_relabeling = {"Water Lily_vtd": "Water Lily VTD",
                        "Court Map_vtd": "Remedial Map (Motown Sound) VTD",
                        "Daisy 2_vtd": "Daisy 2 VTD",
                        "MI-HD-2022_vtd": "Invalidated Map VTD",
                        "Trillium_vtd": "Trillium VTD",
                        "Palm_vtd": "Palm VTD",
                        "MI-SD-2022_vtd": "Invalidated Map VTD",
                        "Linden_vtd": "Linden VTD",
                        "Cherry v2_vtd": "Cherry v2 VTD",
                        "MI-CD-2022_vtd": "Enacted Map VTD",
                        "Apple v2_vtd": "Apple v2 VTD",
                        "Birch v2_vtd": "Birch v2 VTD",
                        "Final Chestnut_vtd": "Chestnut VTD"
                        }
number_fixed_districts = {"house_1": 97, "house_2": 95, "senate":30 }

invalidated_maps = {"state_house": "MI-HD-2022_vtd",
                    "state_senate": "MI-SD-2022_vtd",
                    "congress": "MI-CD-2022_vtd"}

def sort_elections(elec_list):
    """
    Helper function to sort elections chronologically for plotting. Assumes the last two characters
    in the election name are the year, e.g. "SEN18"
    """
    tuplified_elecs = list(map(lambda x: (x[:-2], x[-2:]), sorted(elec_list)))
    sorted_tuples = sorted(tuplified_elecs, key=lambda x: x[1])
    return [tup[0] + tup[1] for tup in sorted_tuples]

# for DF
data = {}

print("invalidated maps")
# invalidated map stats
for map_type in ["state_house", "state_senate", "congress"]:
    proposed_plans = f"Michigan/plan_stats/{map_type}_proposed_plans.jsonl"
    proposed_list = []
    if os.path.exists(proposed_plans):
        with open(proposed_plans, "rb") as fp:
            proposed_list = list(fp)
    invalidated_map = [json.loads(j) for j in proposed_list if json.loads(j)["type"] == "proposed_plan" and json.loads(j)["name"] ==invalidated_maps[map_type]][0]
    invalidated_name = map_name_relabeling[invalidated_maps[map_type]]

    # init plan data
    plan_data = {"# Districts Scrambled": 0, 
                "# Districts Fixed": len(invalidated_map["TOTPOP"]),
                f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While OEG Serial Beats State": "0", 
                f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While |OEG Serial| < .04": "0" if abs(invalidated_map["avg_efficiency_gap"]) >= .04 else f"{invalidated_map[f'num_vra_effective_bvap_{bvap_thresh}_biden_{biden_thresh}']}", #compute 
                f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While SEG Serial Beats State": "0", 
                f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While |SEG Serial| < .04": "0" if abs(invalidated_map["avg_s_efficiency_gap"]) >= .04 else f"{invalidated_map[f'num_vra_effective_bvap_{bvap_thresh}_biden_{biden_thresh}']}", #compute 
                }

    # election indices
    for i in [0,1,3]:
        plan_data.update({
                            f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While OEG Index {i} Beats State": "0",
                            f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While |OEG Index {i}| < .04": "0" if abs(invalidated_map["efficiency_gap"][f"Index_{i}"]) >= .04 else f"{invalidated_map[f'num_vra_effective_bvap_{bvap_thresh}_biden_{biden_thresh}']}",
                            f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While SEG Index {i} Beats State": "0",
                            f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While |SEG Index {i}| < .04": "0" if abs(invalidated_map["s_efficiency_gap"][f"Index_{i}"]) >= .04 else f"{invalidated_map[f'num_vra_effective_bvap_{bvap_thresh}_biden_{biden_thresh}']}",
                            })
    

    # print("plan data",plan_data)
    data[f"{map_type_relabeling[map_type]} {invalidated_name}"] = plan_data

print("full scrambles")
# ensembles of full scrambles
for map_type in ["state_house", "state_senate", "congress"]:
    if "house" in map_type:
        region_aware_str = f"county_and_sub_aware_w{.33}_{.33}"
        epsilon = .05
    elif "senate" in map_type:
        region_aware_str = f"county_and_sub_aware_w{.33}_{.66}"
        epsilon = .05
    else:
        region_aware_str = f"county_and_sub_aware_w{.66}_{.66}"
        epsilon = .01


    method = f"{region_aware_str}_vra_neutral_theta_2.0_bvap_{bvap_thresh}_biden_{biden_thresh}"
    with gzip.open(f"Michigan/ensemble_stats/michigan_{map_type}_{epsilon}_bal_100000_steps_{method}.jsonl.gz", "rb") as fe:
        ensemble_list = list(fe)[:TESTING_TRUNCATOR]
    ensemble_plans = [json.loads(j) for j in ensemble_list if json.loads(j)["type"] == "ensemble_plan"]

    proposed_plans = f"Michigan/plan_stats/{map_type}_proposed_plans.jsonl"
    proposed_list = []
    if os.path.exists(proposed_plans):
        with open(proposed_plans, "rb") as fp:
            proposed_list = list(fp)
    invalidated_map = [json.loads(j) for j in proposed_list if json.loads(j)["type"] == "proposed_plan" and json.loads(j)["name"] ==invalidated_maps[map_type]][0]

    # print("OEG invaid", invalidated_map['avg_efficiency_gap'])
    # print("SEG invalid", invalidated_map['avg_s_efficiency_gap'])
    
    try:
        vra_eg_state = f"{max([plan['num_vra_effective'] for plan in ensemble_plans if abs(plan['avg_efficiency_gap']) < abs(invalidated_map['avg_efficiency_gap']) ])}"
    except ValueError as e:
        if "arg is an empty sequence" in str(e):
            vra_eg_state = "0"
        else:
            raise e
    
    try:
        vra_eg_04 = f"{max([plan['num_vra_effective'] for plan in ensemble_plans if abs(plan['avg_efficiency_gap']) < .04 ])}"
    except ValueError as e:
        if "arg is an empty sequence" in str(e):
            vra_eg_04 = "0"
        else:
            raise e
    
    try:
        vra_seg_state = f"{max([plan['num_vra_effective'] for plan in ensemble_plans if abs(plan['avg_s_efficiency_gap']) < abs(invalidated_map['avg_s_efficiency_gap']) ])}"
    except ValueError as e:
        if "arg is an empty sequence" in str(e):
            vra_seg_state = "0"
        else:
            raise e
        
    try:
        vra_seg_04 = f"{max([plan['num_vra_effective'] for plan in ensemble_plans if abs(plan['avg_s_efficiency_gap']) < .04 ])}"
    except ValueError as e:
        if "arg is an empty sequence" in str(e):
            vra_seg_04 = "0"
        else:
            raise e



    plan_data = {"# Districts Scrambled": len(ensemble_plans[0]["TOTPOP"]), 
                "# Districts Fixed": "0",
                f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While OEG Serial Beats State": vra_eg_state, 
                f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While |OEG Serial| < .04": vra_eg_04, 
                f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While SEG Serial Beats State": vra_seg_state, 
                f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While |SEG Serial| < .04": vra_seg_04, 
                }

    # election indices
    for i in [0,1,3]:
        try:
            vra_eg_state = f"{max([plan['num_vra_effective'] for plan in ensemble_plans if abs(plan['efficiency_gap'][f'Index_{i}']) < abs(invalidated_map['efficiency_gap'][f'Index_{i}']) ])}"
        except ValueError as e:
            if "arg is an empty sequence" in str(e):
                vra_eg_state = "0"
            else:
                raise e
        
        try:
            vra_eg_04 = f"{max([plan['num_vra_effective'] for plan in ensemble_plans if abs(plan['efficiency_gap'][f'Index_{i}']) < .04 ])}"
        except ValueError as e:
            if "arg is an empty sequence" in str(e):
                vra_eg_04 = "0"
            else:
                raise e
        
        try:
            vra_seg_state = f"{max([plan['num_vra_effective'] for plan in ensemble_plans if abs(plan['s_efficiency_gap'][f'Index_{i}']) < abs(invalidated_map['s_efficiency_gap'][f'Index_{i}']) ])}"
        except ValueError as e:
            if "arg is an empty sequence" in str(e):
                vra_seg_state = "0"
            else:
                raise e
            
        try:
            vra_seg_04 = f"{max([plan['num_vra_effective'] for plan in ensemble_plans if abs(plan['s_efficiency_gap'][f'Index_{i}']) < .04 ])}"
        except ValueError as e:
            if "arg is an empty sequence" in str(e):
                vra_seg_04 = "0"
            else:
                raise e
        plan_data.update({
                            f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While OEG Index {i} Beats State": vra_eg_state,
                            f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While |OEG Index {i}| < .04": vra_eg_04,
                            f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While SEG Index {i} Beats State": vra_seg_state,
                            f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While |SEG Index {i}| < .04": vra_seg_04,
                            })

    # print("plan data",plan_data)
    data[f"{map_type_relabeling[map_type]} Full Run"] = plan_data



# ensembles of partial scrambles
print("partial scrambles")
for map_type in ["house_1", "house_2", "senate"]:
    region_aware_str = f"county_sub_aware_w{.66}"
    method = f"{region_aware_str}_vra_neutral_theta_2.0_bvap_{bvap_thresh}_biden_{biden_thresh}"
    with gzip.open(f"Michigan_restricted/ensemble_stats/michigan_restricted_{map_type}_0.05_bal_100000_steps_{method}.jsonl.gz", "rb") as fe:
        partial_ensemble_list = list(fe)[:TESTING_TRUNCATOR]
    with gzip.open(f"Michigan_embed/ensemble_stats/michigan_embed_{map_type}_0.05_bal_100000_steps_{method}.jsonl.gz", "rb") as fe:
        embed_ensemble_list = list(fe)[:TESTING_TRUNCATOR]


    partial_ensemble_plans = [json.loads(j) for j in partial_ensemble_list if json.loads(j)["type"] == "ensemble_plan"]
    embed_ensemble_plans = [json.loads(j) for j in embed_ensemble_list if json.loads(j)["type"] == "ensemble_plan"]
 
    if "house" in map_type:
        full_map = "state_house"
    else:
        full_map = "state_senate"
    
    

    proposed_plans = f"Michigan/plan_stats/{full_map}_proposed_plans.jsonl"
    proposed_list = []
    if os.path.exists(proposed_plans):
        with open(proposed_plans, "rb") as fp:
            proposed_list = list(fp)
    invalidated_map = [json.loads(j) for j in proposed_list if json.loads(j)["type"] == "proposed_plan" and json.loads(j)["name"] ==invalidated_maps[full_map]][0]

    
    try:
        vra_eg_state = f"{max([plan['num_vra_effective'] for plan in embed_ensemble_plans if abs(plan['avg_efficiency_gap']) < abs(invalidated_map['avg_efficiency_gap']) ])}"
    except ValueError as e:
        if "arg is an empty sequence" in str(e):
            vra_eg_state = "0"
        else:
            raise e
    
    try:
        vra_eg_04 = f"{max([plan['num_vra_effective'] for plan in embed_ensemble_plans if abs(plan['avg_efficiency_gap']) < .04 ])}"
    except ValueError as e:
        if "arg is an empty sequence" in str(e):
            vra_eg_04 = "0"
        else:
            raise e
    
    try:
        vra_seg_state = f"{max([plan['num_vra_effective'] for plan in embed_ensemble_plans if abs(plan['avg_s_efficiency_gap']) < abs(invalidated_map['avg_s_efficiency_gap']) ])}"
    except ValueError as e:
        if "arg is an empty sequence" in str(e):
            vra_seg_state = "0"
        else:
            raise e
        
    try:
        vra_seg_04 = f"{max([plan['num_vra_effective'] for plan in embed_ensemble_plans if abs(plan['avg_s_efficiency_gap']) < .04 ])}"
    except ValueError as e:
        if "arg is an empty sequence" in str(e):
            vra_seg_04 = "0"
        else:
            raise e

    plan_data = {"# Districts Scrambled": len(partial_ensemble_plans[0]["TOTPOP"]), 
                "# Districts Fixed": len(embed_ensemble_plans[0]["TOTPOP"])-len(partial_ensemble_plans[0]["TOTPOP"]),
                f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While OEG Serial Beats State": vra_eg_state, 
                f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While |OEG Serial| < .04": vra_eg_04, 
                f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While SEG Serial Beats State": vra_seg_state, 
                f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While |SEG Serial| < .04": vra_seg_04, 
                }
    # election indices
    for i in [0,1,3]:
        try:
            vra_eg_state = f"{max([plan['num_vra_effective'] for plan in embed_ensemble_plans if abs(plan['efficiency_gap'][f'Index_{i}']) < abs(invalidated_map['efficiency_gap'][f'Index_{i}']) ])}"
        except ValueError as e:
            if "arg is an empty sequence" in str(e):
                vra_eg_state = "0"
            else:
                raise e
        
        try:
            vra_eg_04 = f"{max([plan['num_vra_effective'] for plan in embed_ensemble_plans if abs(plan['efficiency_gap'][f'Index_{i}']) < .04 ])}"
        except ValueError as e:
            if "arg is an empty sequence" in str(e):
                vra_eg_04 = "0"
            else:
                raise e
        
        try:
            vra_seg_state = f"{max([plan['num_vra_effective'] for plan in embed_ensemble_plans if abs(plan['s_efficiency_gap'][f'Index_{i}']) < abs(invalidated_map['s_efficiency_gap'][f'Index_{i}']) ])}"
        except ValueError as e:
            if "arg is an empty sequence" in str(e):
                vra_seg_state = "0"
            else:
                raise e
            
        try:
            vra_seg_04 = f"{max([plan['num_vra_effective'] for plan in embed_ensemble_plans if abs(plan['s_efficiency_gap'][f'Index_{i}']) < .04 ])}"
        except ValueError as e:
            if "arg is an empty sequence" in str(e):
                vra_seg_04 = "0"
            else:
                raise e
        plan_data.update({
                            f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While OEG Index {i} Beats State": vra_eg_state,
                            f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While |OEG Index {i}| < .04": vra_eg_04,
                            f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While SEG Index {i} Beats State": vra_seg_state,
                            f"Max # of VRA ({bvap_thresh}, {biden_thresh}) While |SEG Index {i}| < .04": vra_seg_04,
                            })
    # print("plan data",plan_data)
    data[f"{map_type_relabeling[map_type]} Scramble Run"] = plan_data



# keys of dictionary act as columns
df = pd.DataFrame.from_dict(data, orient="columns")

if TESTING_TRUNCATOR == 100000:
    df.to_csv(f"Tables/vra_and_eg_table_biden_{biden_thresh}_bvap_{bvap_thresh}.csv")
else:
    print("used truncator")
    df.to_csv(f"Tables/TEST_{TESTING_TRUNCATOR}_vra_and_eg_table_biden_{biden_thresh}_bvap_{bvap_thresh}.csv")
print("done")