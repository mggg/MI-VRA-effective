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
parser.add_argument("hot", metavar="hot", type=int,
                    help="number of hot steps",
                    default = 0)
parser.add_argument("cold", metavar="cold", type=int,
                    help="number of cold steps",
                    default = 0)
parser.add_argument("beta_magnitude", metavar="beta_magnitude", type=float,
                    help="scaling factor to weight changes in score; large means lower acceptance prob",
                    default = 0.0)

args = parser.parse_args()

## Read in args and state specifications
state = "Michigan"
plan_type = args.map
steps = args.n
county_weight = args.county_weight
county_sub_weight = args.county_sub_weight
hot = args.hot
cold = args.cold
beta_magnitude = args.beta_magnitude


region_aware_str = f"cw_{county_weight}_csw_{county_sub_weight}"

opt_str = f"anneal_hot_{hot}_cold_{cold}_beta_mag_{beta_magnitude}"


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

rec.record_chain(k, eps, steps, chain_name, hot=hot, cold=cold, beta_magnitude=beta_magnitude)

print("done")