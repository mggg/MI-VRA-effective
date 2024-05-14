import matplotlib.pyplot as plt
import sys
import json
from configuration import *
from plotting_class import PlotFactory
state = "Michigan_embed"
n = 100000

TESTING = False
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
    FIG_DIR = f"Figures/restricted_for_paper"
if "house" in plan_type:    
    title = f"{plan_type.capitalize()}"
else:
    title = f"Senate_1"
file_suffix = f"Michigan_embed_{plan_type}_CW_{county_weight}_CSW_{county_sub_weight}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}.png"

fig, axes  = plt.subplots(figsize=(6,4))

vra_strs = ["vra_neutral", "vra_climb"]
proposed = False
for i,vra_str in enumerate(vra_strs):
    if i == len(vra_strs) -1 :
        proposed = True
    print(vra_str)
    if vra_str == "vra_climb":
        method = f"{region_aware_str}_{vra_str}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}"
    else:
        method = f"{region_aware_str}_{vra_str}_theta_{2.0}_bvap_{bvap_thresh}_biden_{biden_thresh}"
    
    print(method)

    if "house" in plan_type:
        map_type = "state_house"
    else:
        map_type =  "state_senate"

    factory = PlotFactory(state, plan_type, bvap_thresh, biden_thresh, steps = n, method=method,
                    ensemble_dir = f"{state}/ensemble_stats",
                    proposed_plans_file = f"Michigan/plan_stats/{map_type}_proposed_plans.jsonl",
                    output_dir="plots"
                    )
    print("loaded stats")

    # deals with overlapping 3 scatterplots and my plot_scatter method in plotting_class
    if i == 0:
        scores = factory.aggregate_score("num_vra_effective", kind="proposed")
        axes.set_yticks([int(scores[0])], [f"{int(scores[0])}"])

    if index == 47:
        axes = factory.plot(stat, kinds=["ensemble", "proposed"], score_2="num_vra_effective", 
                            my_ax = axes, jitter = True, proposed = proposed)

        axes.tick_params(axis='x', labelrotation=90)
    else:
        
        axes = factory.plot(stat, election=f"Index_{index}", kinds=["ensemble", "proposed"], score_2="num_vra_effective", 
                            my_ax = axes, jitter = True, proposed = proposed)
        axes.tick_params(axis='x', labelrotation=90)
        if "house" in plan_type:
            axes.set_xlabel(f"{stat} Index {index}", labelpad=12)
        else:
            axes.set_xlabel(f"{stat} Index {index}")
    
    
    


def legend_without_duplicate_labels(ax):
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    ax.legend(*zip(*unique), loc='center left', bbox_to_anchor=(1, 0.5))

if with_decoration:
    axes.set_title(title, fontsize=24)
    legend_without_duplicate_labels(axes)
    file_suffix= "with_decoration_"+file_suffix
plt.tight_layout()
if index == 47:
    plt.savefig(f"{FIG_DIR}/Scatter_{stat}_VRA_{file_suffix}", dpi=150)
else:
    plt.savefig(f"{FIG_DIR}/Scatter_{stat}_index_{index}_VRA_{file_suffix}", dpi=150)
plt.close()




print("done")



