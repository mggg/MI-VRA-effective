from gerrychain import Graph, Election, Partition
from gerrychain.updaters import Tally
import pandas as pd
from record_chains_gingle import ChainRecorder
import argparse
import json
from configuration import *
import random
from pathlib import Path



random.seed(4747)


parser = argparse.ArgumentParser(description="VTD Ensemble Recorder", 
                                 prog="run_ensemble.py")
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
parser.add_argument("tilt_prob", metavar="tilt_prob", type=float,
                    help="tilt acceptance probability",
                    default = 0.0)
parser.add_argument("burst_length", metavar="burst_length", type=int,
                    help="short burst length",
                    default = 0)

args = parser.parse_args()

## Read in args and state specifications
state = "Michigan"
plan_type = args.map
steps = args.n
county_weight = args.county_weight
county_sub_weight = args.county_sub_weight
tilt_prob = args.tilt_prob
burst_length = args.burst_length


region_aware_str = f"cw_{county_weight}_csw_{county_sub_weight}"

if burst_length and not tilt_prob:
    opt_str  = f"burst_{burst_length}"
elif not burst_length and tilt_prob:
    opt_str  = f"tilt_{tilt_prob}"
elif not burst_length and not tilt_prob:
    opt_str = "var_burst"
else:
    opt_str = f"burst_{burst_length}_tilt{tilt_prob}"


output_dir = f"{state}_gingles/{CHAIN_DIR}/{steps}"
directory = Path(output_dir)
# Create the directory
directory.mkdir(parents=True, exist_ok=True)

with open("{}/{}.json".format(STATE_SPECS_DIR, state)) as fin:
    state_specification = json.load(fin)

k = state_specification["districts"][plan_type]
eps = state_specification["epsilons"][plan_type]
dual_graph_file = f"{DUAL_GRAPH_DIR}/{state_specification['dual_graph'][plan_type]}"
graph = Graph.from_json(dual_graph_file)
pop_col = state_specification["pop_col"]
county_col = state_specification["county_col"]
cousub_col = state_specification["municipal_col"]
weight_dict = {county_col: county_weight, cousub_col:county_sub_weight}

chain_name = f"{state.lower()}_{plan_type}_{eps}_bal_{steps}_steps_{region_aware_str}_opt_{opt_str}.chain"
print(chain_name)

## Run and Record Chain
rec = ChainRecorder(graph, output_dir, pop_col, weight_dict)

rec.record_chain(k, eps, steps, chain_name, tilt_prob = tilt_prob, burst_length = burst_length)

print("done")