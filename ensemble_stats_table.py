import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import gzip 

# make smaller for faster runs, but not getting full ensemble
TESTING_TRUNCATOR = 100000

# CHECK THIS CODE FOR TODO NOTES

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
                        "MI-CD-2022_vtd": "Enacted Map VTD"
                        }
# number_fixed_districts = {"house_1": 97, "house_2": 95, "senate":30 }

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
                "# Counties Split by Scramble": "N/A", 
                "# Cousub Split by Scramble": "N/A",
                "# Counties Split by Full Map": int(invalidated_map["num_split_counties"]),
                "# Cousubs Split by Full Map": int(invalidated_map["num_split_municipalities"]),
                "# VRA Effective (44, 50)": int(invalidated_map["num_vra_effective_bvap_0.44_biden_0.5"]),
                "# VRA Effective (40, 50)": int(invalidated_map["num_vra_effective_bvap_0.4_biden_0.5"]),
                "# VRA Effective (40, 48)": int(invalidated_map["num_vra_effective_bvap_0.4_biden_0.48"])}


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

    bvap_thresh = .44
    biden_thresh = .5
    

    method = f"{region_aware_str}_vra_neutral_theta_2.0_bvap_{bvap_thresh}_biden_{biden_thresh}"
    with gzip.open(f"Michigan/ensemble_stats/michigan_{map_type}_{epsilon}_bal_100000_steps_{method}.jsonl.gz", "rb") as fe:
        ensemble_list = list(fe)[:TESTING_TRUNCATOR]
    ensemble_plans = [json.loads(j) for j in ensemble_list if json.loads(j)["type"] == "ensemble_plan"]

    
    plan_data = {"# Districts Scrambled": len(ensemble_plans[0]["TOTPOP"]), # number
                "# Districts Fixed": 0, # number 
                "# Counties Split by Scramble": "N/A", 
                "# Cousub Split by Scramble": "N/A", 
                "# Counties Split by Full Map": f"({min([plan['num_split_counties'] for plan in ensemble_plans])}, {max([plan['num_split_counties'] for plan in ensemble_plans])})", # range
                "# Cousubs Split by Full Map": f"({min([plan['num_split_municipalities'] for plan in ensemble_plans])}, {max([plan['num_split_municipalities'] for plan in ensemble_plans])})",# range
                "# VRA Effective (44, 50)": f"({min([plan['num_vra_effective'] for plan in ensemble_plans])}, {max([plan['num_vra_effective'] for plan in ensemble_plans])})" # range
                
                }
    
    
    bvap_thresh = .4
    
    for biden_thresh in [48, 50]:
        try:
            method = f"{region_aware_str}_vra_neutral_theta_2.0_bvap_{bvap_thresh}_biden_{biden_thresh/100.0}"
            with gzip.open(f"Michigan/ensemble_stats/michigan_{map_type}_{epsilon}_bal_100000_steps_{method}.jsonl.gz", "rb") as fe:
                ensemble_list = list(fe)

            ensemble_plans = [json.loads(j) for j in ensemble_list[:TESTING_TRUNCATOR] if json.loads(j)["type"] == "ensemble_plan"]
            plan_data[f"# VRA Effective (40, {biden_thresh})"] = f"({min([plan['num_vra_effective'] for plan in ensemble_plans])}, {max([plan['num_vra_effective'] for plan in ensemble_plans])})" # range
        except:
            print(map_type, "failed for other biden and bvap thresh")

    data[f"{map_type_relabeling[map_type]} Full Run"] = plan_data



# ensembles of partial scrambles
print("partial scrambles")
for map_type in ["house_1", "house_2", "senate"]:

    region_aware_str = f"county_sub_aware_w{.66}"

    bvap_thresh = .44
    biden_thresh = .5
    

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
    invalidated_name = map_name_relabeling[invalidated_maps[full_map]]
    num_vra_full_4450 = data[f"{map_type_relabeling[full_map]} {invalidated_name}"]["# VRA Effective (44, 50)"]
    

    proposed_plans = f"Michigan_restricted/plan_stats/{map_type}_proposed_plans.jsonl"
    proposed_list = []
    if os.path.exists(proposed_plans):
        with open(proposed_plans, "rb") as fp:
            proposed_list = list(fp)
    invalidated_map = [json.loads(j) for j in proposed_list if json.loads(j)["type"] == "proposed_plan"][0]
    num_vra_partial_4450 = invalidated_map[f"num_vra_effective_bvap_{bvap_thresh}_biden_{biden_thresh}"]
    

    plan_data = {"# Districts Scrambled": len(partial_ensemble_plans[0]["TOTPOP"]), # number
                "# Districts Fixed": len(embed_ensemble_plans[0]["TOTPOP"])-len(partial_ensemble_plans[0]["TOTPOP"]), # number 
                "# Counties Split by Scramble": f"({min([plan['num_split_counties'] for plan in partial_ensemble_plans])}, {max([plan['num_split_counties'] for plan in partial_ensemble_plans])})", # range partial
                "# Cousub Split by Scramble": f"({min([plan['num_split_municipalities'] for plan in partial_ensemble_plans])}, {max([plan['num_split_municipalities'] for plan in partial_ensemble_plans])})", # range partial
                "# Counties Split by Full Map": f"({min([plan['num_split_counties'] for plan in embed_ensemble_plans])}, {max([plan['num_split_counties'] for plan in embed_ensemble_plans])})", # range embed
                "# Cousubs Split by Full Map": f"({min([plan['num_split_municipalities'] for plan in embed_ensemble_plans])}, {max([plan['num_split_municipalities'] for plan in embed_ensemble_plans])})",# range embed
                "# VRA Effective (44, 50)":f"({min([plan['num_vra_effective'] for plan in partial_ensemble_plans])}, {max([plan['num_vra_effective'] for plan in partial_ensemble_plans])}) + {num_vra_full_4450 - num_vra_partial_4450}" , # range partial + number from fixed part of map
    }

    bvap_thresh = .4
    for biden_thresh in [48, 50]:
        num_vra_partial = invalidated_map[f"num_vra_effective_bvap_{bvap_thresh}_biden_{biden_thresh/100.0}"]
        num_vra_full = data[f"{map_type_relabeling[full_map]} {invalidated_name}"][f"# VRA Effective (40, {biden_thresh})"]
        method = f"{region_aware_str}_vra_neutral_theta_2.0_bvap_{bvap_thresh}_biden_{biden_thresh/100.0}"
        with gzip.open(f"Michigan_restricted/ensemble_stats/michigan_restricted_{map_type}_0.05_bal_100000_steps_{method}.jsonl.gz", "rb") as fe:
            partial_ensemble_list = list(fe)[:TESTING_TRUNCATOR]

        partial_ensemble_plans = [json.loads(j) for j in partial_ensemble_list if json.loads(j)["type"] == "ensemble_plan"]
        plan_data[f"# VRA Effective (40, {biden_thresh})"] = f"({min([plan['num_vra_effective'] for plan in partial_ensemble_plans])}, {max([plan['num_vra_effective'] for plan in partial_ensemble_plans])}) + {num_vra_full - num_vra_partial}" # range


    data[f"{map_type_relabeling[map_type]} Scramble Run"] = plan_data



# keys of dictionary act as columns
df = pd.DataFrame.from_dict(data, orient="columns")

df.to_csv("Tables/ensemble_stats_table.csv")
print("done")