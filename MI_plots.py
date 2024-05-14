import matplotlib.pyplot as plt
import sys
import json
from configuration import *
from plotting_class import PlotFactory
state = "Michigan"
n = 100000

args = sys.argv[1:]
plan_type = args[0]
vra_str = args[1]
county_weight = float(args[2])
county_sub_weight = float(args[3])
theta = float(args[4])
bvap_thresh = float(args[5])
biden_thresh = float(args[6])

with open("{}/{}.json".format(STATE_SPECS_DIR, state)) as fin:
    state_specification = json.load(fin)



print(plan_type, vra_str, county_weight, county_sub_weight, theta, bvap_thresh, biden_thresh)


if county_weight and not county_sub_weight:
    region_aware_str = f"county_aware_w{county_weight}"

elif county_sub_weight and not county_weight:
    region_aware_str = f"county_sub_aware_w{county_sub_weight}"

elif county_sub_weight and county_weight:
    region_aware_str = f"county_and_sub_aware_w{county_weight}_{county_sub_weight}"
else:
    region_aware_str= "region_neutral"

# {state.lower()}_{plan_type}_{eps}_bal_{steps}_steps_{region_aware_str}_vra_{vra_string}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}.jsonl.gz"
try:
    factory = PlotFactory(state, plan_type, bvap_thresh, biden_thresh, steps = n, method=f"{region_aware_str}_{vra_str}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}",
                        ensemble_dir = f"{state}/ensemble_stats",
                        proposed_plans_file = f"{state}/plan_stats/{plan_type}_proposed_plans.jsonl",
                        output_dir="plots"
                        )
except:
    factory = PlotFactory(state, plan_type, bvap_thresh, biden_thresh, steps = n, method=f"{region_aware_str}_{vra_str}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}",
                        ensemble_dir = f"{state}/ensemble_stats",
                        proposed_plans_file = f"{state}/plan_stats/{plan_type}_proposed_plans.jsonl",
                        output_dir="plots"
                        )
print("loaded stats")
FIG_DIR = f"Figures/full_for_paper"
# FIG_DIR="Figures/testing"

file_suffix = f"Michigan_{plan_type}_{vra_str}_CW_{county_weight}_CSW_{county_sub_weight}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}.pdf"

# # county
# title = f"CW {county_weight} MW {county_sub_weight}"
# fig, axes  = plt.subplots()
# axes= factory.plot("num_split_counties", kinds=["ensemble" ,"proposed"])
# axes.set_title(title,fontsize=24)
# if plan_type == "state_senate":
#     data_max = 60
#     data_min = 8
# elif plan_type == "state_house":
#     data_max = 72
#     data_min = 24
# else:
#     data_max = 50
#     data_min = 0
# data_step = 2
# axes.set_xlim(data_min, data_max)
# axes.set_xticks([x+.5 for x in range(data_min,data_max,data_step)], [str(x) for x in range(data_min,data_max,data_step)])
# plt.tight_layout()
# plt.savefig(f"{FIG_DIR}/Split_Counties_{file_suffix}")
# plt.close()

# # cousub
# title = f"CW {county_weight} MW {county_sub_weight}"
# fig, axes  = plt.subplots()
# axes = factory.plot("num_split_municipalities", kinds=["ensemble" ,"proposed"])
# axes.set_title(title,fontsize=24)
# if plan_type == "state_senate":
#     data_max = 152
#     data_min = 4
# elif plan_type == "state_house":
#     data_max = 240
#     data_min = 36
# else:
#     data_max = 112
#     data_min = 0

# data_step = int((data_max-data_min)/25)
# axes.set_xlim(data_min, data_max)
# axes.set_xticks([x+.5 for x in range(data_min,data_max,data_step)], [str(x) for x in range(data_min,data_max,data_step)])
# axes.tick_params(axis='x', labelrotation=90)
# plt.tight_layout()
# plt.savefig(f"{FIG_DIR}/Split_Municipalities_{file_suffix}")
# plt.close()

# # vra effective
# title = f"VRA Effective Score ({bvap_thresh},{biden_thresh}), Theta {theta}" if theta!=2 else f"VRA Effective Score ({bvap_thresh},{biden_thresh})"
# fig, axes  = plt.subplots()
# axes= factory.plot("num_vra_effective", kinds=["ensemble" ,"proposed"])
# axes.set_title(title,fontsize=24)
# # data_max = state_specification["districts"][plan_type]
# if plan_type == "state_senate":
#     data_max = 5
#     data_min = 0
# elif plan_type == "state_house":
#     data_max = 15
#     data_min = 4
# else:
#     data_max = 3
#     data_min = 0
# data_step = 2
# axes.set_xlim(data_min, data_max)
# axes.set_xticks([x+.5 for x in range(data_min,data_max,data_step)], [str(x) for x in range(data_min,data_max,data_step)])
# plt.tight_layout()
# plt.savefig(f"{FIG_DIR}/VRA_Effective_{file_suffix}")
# plt.close()


# # efficiency gap
# fig, axes  = plt.subplots()
# axes= factory.plot("efficiency_gap", kinds=["ensemble" ,"proposed"])
# axes.set_title(title,fontsize=24)
# plt.tight_layout()
# plt.savefig(f"{FIG_DIR}/Efficiency_Gap_{file_suffix}")
# plt.close()

# # seats
# fig, axes  = plt.subplots()
# axes= factory.plot("seats", kinds=["ensemble" ,"proposed"])
# axes.set_title(title,fontsize=24)
# plt.tight_layout()
# plt.savefig(f"{FIG_DIR}/Seats_{file_suffix}")
# plt.close()

# # mean median
# fig, axes  = plt.subplots()
# axes= factory.plot("mean_median", kinds=["ensemble" ,"proposed"])
# axes.set_title(title,fontsize=24)
# plt.tight_layout()
# plt.savefig(f"{FIG_DIR}/Mean_median_{file_suffix}")
# plt.close()


# # partisan bias
# fig, axes  = plt.subplots()
# axes= factory.plot("partisan_bias", kinds=["ensemble" ,"proposed"])
# axes.set_title(title,fontsize=24)
# plt.tight_layout()
# plt.savefig(f"{FIG_DIR}/Partisan_bias_{file_suffix}")
# plt.close()

# competitive contests
# fig, axes  = plt.subplots()
# axes= factory.plot("num_competitive_districts", kinds=["ensemble" ,"proposed"])
# axes.set_title(title,fontsize=24)

# if plan_type == "state_senate":
#     data_max = 200
# elif plan_type == "state_house":
#     data_max = 1000
# else:
#     data_max = 200
# data_min = 0
# data_step = int((data_max-data_min)/25)
# axes.set_xlim(0, data_max)
# axes.set_xticks([x+.5 for x in range(data_min,data_max,data_step)], [str(x) for x in range(data_min,data_max,data_step)])
# plt.tight_layout()
# plt.savefig(f"{FIG_DIR}/Num_Competitive_{file_suffix}")
# plt.close()

# bvap
fig, axes  = plt.subplots()
title = f"Theta {theta}" if theta!=2 else f"Neutral"
axes= factory.plot("BVAP", kinds=["ensemble" ,"proposed"])
axes.set_title(title,fontsize=24)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/BVAP_{file_suffix}")
plt.close()


# sea level
fig, axes  = plt.subplots()
axes= factory.plot_sea_level()
axes.set_xticks(axes.get_xticks(), axes.get_xticklabels(), rotation=90)
axes.set_title(f"Sea Level Plot for {plan_type.capitalize()}", fontsize=24)

plt.tight_layout()
plt.savefig(f"{FIG_DIR}/Sea_level_michigan_{plan_type}.pdf")
plt.close()

# # scatterplots
# # average efficiency gap
# fig, axes  = plt.subplots()
# axes.set_title(title,fontsize=24)
# plt.tight_layout()
# plt.savefig(f"{FIG_DIR}/Scatter_EG_VRA_{file_suffix}")
# plt.close()


# competitve
# fig, axes  = plt.subplots()
# axes= factory.plot("num_competitive_districts", kinds=["ensemble", "proposed"], score_2="num_vra_effective")
# axes.set_title(title,fontsize=24)
# plt.legend()
# plt.tight_layout()
# plt.savefig(f"{FIG_DIR}/Scatter_Competitive_VRA_{file_suffix}")
# plt.close()


# bvap table for jon
# factory.bvap_table_to_csv(file_name=f"Tables/{state}/bvap_table_{state}_{plan_type}_{vra_str}_CW_{county_weight}_CSW_{county_sub_weight}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}.csv")


print("done")



