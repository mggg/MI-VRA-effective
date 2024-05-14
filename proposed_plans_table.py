import pandas as pd
import os
import json
import matplotlib.pyplot as plt

map_type_relabeling = {"state_house": "HD", "state_senate": "SD", "congress": "CD"}
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


def sort_elections(elec_list):
    """
    Helper function to sort elections chronologically for plotting. Assumes the last two characters
    in the election name are the year, e.g. "SEN18"
    """
    tuplified_elecs = list(map(lambda x: (x[:-2], x[-2:]), sorted(elec_list)))
    sorted_tuples = sorted(tuplified_elecs, key=lambda x: x[1])
    return [tup[0] + tup[1] for tup in sorted_tuples]

data = {}
for map_type in ["state_house", "state_senate", "congress"]:
    proposed_plans = f"Michigan/plan_stats/{map_type}_proposed_plans.jsonl"
    proposed_list = []
    if os.path.exists(proposed_plans):
        with open(proposed_plans, "rb") as fp:
            proposed_list = list(fp)
        proposed_summary = json.loads(proposed_list[0])
        proposed_election_names = sort_elections(election["name"] for election in proposed_summary["elections"])
    proposed_plans = [json.loads(j) for j in proposed_list if json.loads(j)["type"] == "proposed_plan"]
    proposed_names = [proposed_plan["name"] for proposed_plan in proposed_plans]


    for plan, name in zip(proposed_plans, proposed_names):  
        plan_data = {}
        plan_data["Split Counties"]= int(plan["num_split_counties"])
        plan_data["Split Municipalities"]= int(plan["num_split_municipalities"])
        plan_data["# VRA Effective (44, 50)"]= int(plan["num_vra_effective_bvap_0.44_biden_0.5"])
        plan_data["# VRA Effective (40, 50)"]= int(plan["num_vra_effective_bvap_0.4_biden_0.5"])
        plan_data["# VRA Effective (40, 48)"]= int(plan["num_vra_effective_bvap_0.4_biden_0.48"])
        plan_data["Avg. OEG"] = round(plan["avg_efficiency_gap"],3)
        plan_data["Avg. SEG"] = round(plan["avg_s_efficiency_gap"],3)
        plan_data["Avg. MM"] = round(plan["avg_mean_median"],3)
        plan_data["Avg. LM"] = round(plan["avg_lopsided_margin"],3)
        plan_data["Mean Disprop."] = round(plan["mean_disprop"],3)
        plan_data["# Dem. Seats in PRES16"] = int(plan["num_d_seats_pres_16"])
        for i in [0,1,3]:
            plan_data[f"OEG Index {i}"] = round(plan["efficiency_gap"][f"Index_{i}"],3)
            plan_data[f"SEG Index {i}"] = round(plan["s_efficiency_gap"][f"Index_{i}"],3)
            plan_data[f"MM Index {i}"] = round(plan["mean_median"][f"Index_{i}"],3)
            plan_data[f"LM Index {i}"] = round(plan["lopsided_margin"][f"Index_{i}"],3)
            plan_data[f"Disprop. Index {i}"] = round(plan["disprop"][f"Index_{i}"],3)

        data[f"{map_type_relabeling[map_type]} {map_name_relabeling[name]}"] = plan_data

# keys of dictionary act as columns
df = pd.DataFrame.from_dict(data, orient="columns")
df.to_csv("Tables/proposed_plans_table.csv")