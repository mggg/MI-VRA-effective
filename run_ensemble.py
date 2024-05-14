from gerrychain import Graph, Election, Partition
from gerrychain.updaters import Tally
import pandas as pd
from record_chains import ChainRecorder
import argparse
import json
from configuration import *
from vra import num_effective_districts

import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description="VTD Ensemble Recorder", 
                                 prog="run_ensemble.py")
parser.add_argument("st", metavar="state", type=str,
                    choices=SUPPORTED_STATES,
                    help="Which state to run the ensemble on?")
parser.add_argument("map", metavar="map", type=str,
                    choices=SUPPORTED_PLAN_TYPES,
                    help="the map to redistrict")
parser.add_argument("n", metavar="iterations", type=int,
                    help="the number of steps to take")
parser.add_argument("county_weight", metavar="county_weight", type=float,
                    help="the weight to add to counties for region aware",
                    default = 0.0)
parser.add_argument("county_sub_weight", metavar="county_sub_weight", type=float,
                    help="the weight to add to counties for region aware",
                    default = 0.0)
parser.add_argument("theta", metavar="theta", type=float,
                    help="MH theta parameter",
                    default = 2.0)
parser.add_argument("bvap", metavar="bvap", type=float,
                    help="the threshold percent for bvap in VRA effective (.43)",
                    default = 0.4)
parser.add_argument("biden", metavar="biden", type=float,
                    help="the threshold percent for biden in VRA effective (.53)",
                    default = 0.5)
parser.add_argument("--VRA_reject", action='store_const', const=True, default=False,
                    dest="VRA_reject",
                    help="Chain only accepts maps above threshold number of effective districts? (default False)")
parser.add_argument("--VRA_climb", action='store_const', const=True, default=False,
                    dest="VRA_climb",
                    help="Chain uses MH acceptance rule for number of effective districts? (default False)")
parser.add_argument("--quiet", dest="verbosity", action="store_const", const=None, default=1000,
                    help="Silence * tracker of chain position?")
args = parser.parse_args()

## Read in args and state specifications
state = args.st
plan_type = args.map
steps = args.n
county_weight = args.county_weight
county_sub_weight = args.county_sub_weight
theta = args.theta
bvap_thresh = args.bvap
biden_thresh = args.biden
vra_reject = args.VRA_reject
vra_climb = args.VRA_climb

if county_weight and not county_sub_weight:
    region_aware_str = f"county_aware_w{county_weight}"

elif county_sub_weight and not county_weight:
    region_aware_str = f"county_sub_aware_w{county_sub_weight}"

elif county_sub_weight and county_weight:
    region_aware_str = f"county_and_sub_aware_w{county_weight}_{county_sub_weight}"
else:
    region_aware_str= "region_neutral"

if vra_reject and vra_climb:
    raise ValueError("Cannot run vra reject and climb concurrently.")

elif vra_reject:
    vra_string = "reject"

elif vra_climb:
    vra_string = "climb"

else:
    vra_string = "neutral"




output_dir = "{}/{}".format(state, CHAIN_DIR)
verbose_freq = args.verbosity

with open("{}/{}.json".format(STATE_SPECS_DIR, state)) as fin:
    state_specification = json.load(fin)

k = state_specification["districts"][plan_type]
eps = state_specification["epsilons"][plan_type]
dual_graph_file = "{}/{}".format(DUAL_GRAPH_DIR, state_specification["dual_graph"][plan_type])
pop_col = state_specification["pop_col"]
county_col = state_specification["county_col"]
cousub_col = state_specification["municipal_col"]


graph = Graph.from_json(dual_graph_file)

# VRA rejection threshold will be computed based on enacted map
if plan_type == "congress":
    file_name = "MI-CD-2022_vtd.csv"
elif plan_type == "state_house":
    file_name = "MI-HD-2022_vtd.csv"
elif plan_type == "state_senate":
    file_name = "MI-SD-2022_vtd.csv"

plan = pd.read_csv(f"Michigan/proposed_plans/vtd_level/{plan_type}/{file_name}", dtype={"GEOID20": "str", "assignment": int}).set_index("GEOID20").to_dict()['assignment']
ddict = {n: plan[graph.nodes()[n]["GEOID20"]] for n in graph.nodes()}

updaters  = {"population": Tally(pop_col, alias="population"),
                            "PRES20": Election("PRES20", {"Democratic": "G20PREDBID", "Republican": "G20PRERTRU"}),
                            "BVAP": Tally("BVAP", alias="BVAP"),
                            "VAP": Tally("VAP", alias="VAP")}



part = Partition(graph, ddict, updaters)
vra_threshold = num_effective_districts(part, bvap_thresh, biden_thresh)


weight_dict = {county_col: county_weight, cousub_col:county_sub_weight}


## Run and Record Chain
rec = ChainRecorder(graph, output_dir, pop_col, weight_dict, vra_threshold, verbose_freq=verbose_freq,
                    theta = theta, bvap_thresh = bvap_thresh, biden_thresh=biden_thresh)

# if "seed_plans" in state_specification and plan_type in state_specification["seed_plans"]:
#     seed_plan_path = state_specification["seed_plans"][plan_type] 
#     seed_plan = pd.read_csv(f"seed_plans/{seed_plan_path}", dtype={"GEOID20": "str", "assignment": int}).set_index("GEOID20").to_dict()['assignment']
#     ddict = {n: seed_plan[graph.nodes()[n]["GEOID20"]] for n in graph.nodes()}
#     seed_plan = rec.get_partition(ddict)
#     print("seeded")
# else:
#     seed_plan = None

rec.record_chain(k, eps, steps,f"{state.lower()}_{plan_type}_{eps}_bal_{steps}_steps_{region_aware_str}_vra_{vra_string}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}.chain",
                         vra_reject = vra_reject, vra_climb = vra_climb,
                         initial_partition=None)

print("done")