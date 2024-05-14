import matplotlib.pyplot as plt
import sys
import json
from configuration import *
from plotting_class import PlotFactory
state = "Michigan"
n = 100000

TESTING =False
with_decoration = True

args = sys.argv[1:]
plan_type = args[0]
county_weight = float(args[1])
county_sub_weight = float(args[2])
theta = float(args[3])
bvap_thresh = float(args[4])
biden_thresh = float(args[5])
stat = args[6]
index = int(args[7])

with open("{}/{}.json".format(STATE_SPECS_DIR, state)) as fin:
    state_specification = json.load(fin)


# print(plan_type, vra_str, county_weight, county_sub_weight, theta, bvap_thresh, biden_thresh)


if county_weight and not county_sub_weight:
    region_aware_str = f"county_aware_w{county_weight}"

elif county_sub_weight and not county_weight:
    region_aware_str = f"county_sub_aware_w{county_sub_weight}"

elif county_sub_weight and county_weight:
    region_aware_str = f"county_and_sub_aware_w{county_weight}_{county_sub_weight}"
else:
    region_aware_str= "region_neutral"

# {state.lower()}_{plan_type}_{eps}_bal_{steps}_steps_{region_aware_str}_vra_{vra_string}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}.jsonl.gz"

if TESTING:
    FIG_DIR = f"Figures/testing"
else:
    FIG_DIR = f"Figures/full_for_paper"
title = f"{plan_type.capitalize()}"

file_suffix = f"Michigan_{plan_type}_CW_{county_weight}_CSW_{county_sub_weight}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}.png"


    
vra_strs = ["vra_neutral", "vra_climb"]

fig, axes  = plt.subplots(figsize=(6,4))
proposed = False
for i,vra_str in enumerate(vra_strs):
    
    if i == len(vra_strs) -1 :
        proposed = True
    if vra_str == "vra_climb":
        method = f"{region_aware_str}_{vra_str}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}"
    else:
        method = f"{region_aware_str}_{vra_str}_theta_{2.0}_bvap_{bvap_thresh}_biden_{biden_thresh}"
    factory = PlotFactory(state, plan_type, bvap_thresh, biden_thresh, steps = n, method=method,
                    ensemble_dir = f"{state}/ensemble_stats",
                    proposed_plans_file = f"{state}/plan_stats/{plan_type}_proposed_plans.jsonl",
                    output_dir="plots"
                    )
    print("loaded stats")

    if i == 0:
        scores = factory.aggregate_score("num_vra_effective", kind="proposed")
        axes.set_yticks([int(scores[0])], [f"{int(scores[0])}"])

    if index == 47:
        axes = factory.plot(stat, kinds=["ensemble", "proposed"], score_2="num_vra_effective", 
                            my_ax = axes, jitter = True, proposed= proposed)
    else:
        axes = factory.plot(stat, election=f"Index_{index}", kinds=["ensemble", "proposed"], score_2="num_vra_effective", 
                            my_ax = axes, jitter = True, proposed= proposed)
        axes.set_xlabel(f"{stat} Index {index}")
    

def legend_without_duplicate_labels(ax):
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    ax.legend(*zip(*unique), loc='center left', bbox_to_anchor=(1, 0.5))

if with_decoration:
    axes.set_title(title, fontsize=24)
    legend_without_duplicate_labels(axes)
    file_suffix= "with_decoration_"+file_suffix
axes.tick_params(axis='x', labelrotation=90)

plt.tight_layout()
if index == 47:
    plt.savefig(f"{FIG_DIR}/Scatter_{stat}_VRA_{file_suffix}", dpi=150)
else:
    plt.savefig(f"{FIG_DIR}/Scatter_{stat}_index_{index}_VRA_{file_suffix}", dpi=150)





print("done")



