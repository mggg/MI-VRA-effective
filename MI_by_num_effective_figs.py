import sys
import gzip
import json
import os
import numpy as np
from plotting_class import PlotFactory
import matplotlib.pyplot as plt

def sort_elections(elec_list):
    """
    Helper function to sort elections chronologically for plotting. Assumes the last two characters
    in the election name are the year, e.g. "SEN18"
    """
    tuplified_elecs = list(map(lambda x: (x[:-2], x[-2:]), sorted(elec_list)))
    sorted_tuples = sorted(tuplified_elecs, key=lambda x: x[1])
    return [tup[0] + tup[1] for tup in sorted_tuples]

args = sys.argv[1:]

state = args[0]
plan_type = args[1]
county_weight = float(args[2])
county_sub_weight = float(args[3])
bvap_thresh = float(args[4])
biden_thresh = float(args[5])
score = args[6]

print(state, plan_type, county_weight, county_sub_weight, bvap_thresh, biden_thresh)

steps = 100000
# set to steps if you want full ensemble
restrict_size = steps

if plan_type == "congress":
    eps = 0.01
elif "senate" in plan_type:
    eps = 0.05
elif "house" in plan_type:
    eps = 0.05


if county_weight and not county_sub_weight:
    region_aware_str = f"county_aware_w{county_weight}"

elif county_sub_weight and not county_weight:
    region_aware_str = f"county_sub_aware_w{county_sub_weight}"

elif county_sub_weight and county_weight:
    region_aware_str = f"county_and_sub_aware_w{county_weight}_{county_sub_weight}"
else:
    region_aware_str= "region_neutral"


vra_effective_to_score = {}
for vra_str in ["vra_neutral", "vra_reject", "vra_climb"]:
    if vra_str == "vra_climb":
        theta = 100.0
    else:
        theta = 2.0
    ensemble_dir =f"{state}/ensemble_stats"
    method = f"{region_aware_str}_{vra_str}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}"
    score_file =f"{state.lower()}_{plan_type}_{eps}_bal_{steps}_steps_{method}.jsonl.gz"

    with gzip.open(f"{ensemble_dir}/{score_file}", "rb") as fe:
        ensemble_list = list(fe)
    ensemble_summary = json.loads(ensemble_list[0])
    ensemble_plans = [json.loads(j) for j in ensemble_list[:restrict_size] if json.loads(j)["type"] == "ensemble_plan"]

    for plan in ensemble_plans:
        if plan["num_vra_effective"] in vra_effective_to_score:
            vra_effective_to_score[plan["num_vra_effective"]].append(plan[score])
        else:
            vra_effective_to_score[plan["num_vra_effective"]] = [plan[score]]

vra_effective_to_score = dict(sorted(vra_effective_to_score.items(), reverse = True))

proposed_list = []

if "house" in plan_type:
    map_type = "state_house"
elif "senate" in plan_type:
    map_type = "state_senate"
else:
    map_type = plan_type

proposed_plans = f"Michigan/plan_stats/{map_type}_proposed_plans.jsonl"
if os.path.exists(proposed_plans):
    with open(proposed_plans, "rb") as fp:
        proposed_list = list(fp)
    proposed_summary = json.loads(proposed_list[0])
    proposed_election_names = sort_elections(election["name"] for election in proposed_summary["elections"])
proposed_plans = [json.loads(j) for j in proposed_list if json.loads(j)["type"] == "proposed_plan"]
proposed_names = [proposed_plan["name"] for proposed_plan in proposed_plans]

factory = PlotFactory(state, plan_type, bvap_thresh, biden_thresh, steps = steps, method=f"{region_aware_str}_{vra_str}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}",
                    ensemble_dir = f"{state}/ensemble_stats",
                    proposed_plans_file = f"Michigan/plan_stats/{map_type}_proposed_plans.jsonl",
                    output_dir="plots"
                    )


FIG_DIR = f"Figures/misc_for_paper"

numplots = len(list(vra_effective_to_score.keys()))


m = 1 # number of columns
n = int(np.ceil(numplots/float(m))) # number of rows

fig, axes = plt.subplots(nrows=n,ncols=m, figsize=(6*m, 6*n), sharex=True, sharey=True)

min_val = min(min(score_list) for score_list in vra_effective_to_score.values())
max_val = max(max(score_list) for score_list in vra_effective_to_score.values())


min_val = min([plan[score] for plan in proposed_plans]+[min_val])
max_val = max([plan[score] for plan in proposed_plans]+[max_val])
if min_val == max_val:
    max_val+=1


# if "house" in plan_type:
#     min_val = 160
#     max_val = 320
# elif "senate" in plan_type:
#     min_val = 29
#     max_val = 149

unique_vals = set().union(*vra_effective_to_score.values())

for (num_effective, score_list), ax in zip(vra_effective_to_score.items(), axes.flatten()):
    scores = {"citizen":[], 
        "ensemble": score_list, 
        "proposed": [], #[plan[score] for plan in proposed_plans if 
                                #plan[f"num_vra_effective_bvap_{bvap_thresh}_biden_{biden_thresh}"]==num_effective]
        }
    
    
    # proposed_plan_labels = [f"{plan['name']}: {round(plan[score],4)}" for plan in proposed_plans if 
    #                             plan[f"num_vra_effective_bvap_{bvap_thresh}_biden_{biden_thresh}"]==num_effective]

    # proposed_plan_colors = [c for i,c in enumerate(factory.proposed_colors[:len(proposed_plans)]) if 
    #                             proposed_plans[i][f"num_vra_effective_bvap_{bvap_thresh}_biden_{biden_thresh}"]==num_effective]

    ax = factory.plot_histogram(ax, score, scores, legend = False, 
                    val_range=(min_val,max_val), 
                    unique_vals = unique_vals,
                    # proposed_plan_labels = proposed_plan_labels,
                    # proposed_plan_colors = proposed_plan_colors,
                    )

    ax.set_title(f"{num_effective} VRA Effective Districts", fontsize=24)
    ax.set_xlabel(score, fontsize = 18)
    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # rotate tick labels
    ax.tick_params(axis='x', labelrotation=90)
    # ax.set_aspect('equal')

# ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
# optionally, remove empty plots from grid
if n*m > numplots:
    for ax in axes.flatten()[numplots:]:
        ax.remove()

# plt.suptitle(f"Michigan {plan_type.capitalize()} CS {county_weight} CSS {county_sub_weight}\n VRA Effective Score ({bvap_thresh},{biden_thresh})\n {score}")
file_suffix = f"{state.lower()}_{plan_type}_CW_{county_weight}_CSW_{county_sub_weight}_bvap_{bvap_thresh}_biden_{biden_thresh}.pdf"
# plt.suptitle(plan_type.capitalize())

plt.tight_layout()
plt.savefig(f"{FIG_DIR}/{score}_split_by_num_effective_{file_suffix}")