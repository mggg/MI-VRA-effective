from gerrychain import Graph, Election, Partition
from gerrychain.updaters import Tally
import pandas as pd
from pcompress import Replay
from record_chains_gingle import ChainRecorder
import argparse
import json
from configuration import *
import random
from pathlib import Path
import csv

state  = "Michigan"
steps = 100000

parser = argparse.ArgumentParser(description="VTD Ensemble Recorder", 
                                 prog="run_ensemble.py")
parser.add_argument("map", metavar="map", type=str,
                    choices=SUPPORTED_PLAN_TYPES,
                    help="the map to redistrict")
parser.add_argument("file_name", metavar="file_name", type=str,
                    help="the name of the pcompress chain")

args = parser.parse_args()
plan_type = args.map
file_name = (args.file_name).split("../")[-1]


with open("{}/{}.json".format(STATE_SPECS_DIR, state)) as fin:
    state_specification = json.load(fin)

dual_graph_file = f"{DUAL_GRAPH_DIR}/{state_specification['dual_graph'][plan_type]}"
graph = Graph.from_json(dual_graph_file)

demographic_updaters = {demo_col: Tally(demo_col, alias=demo_col) for demo_col in ["BVAP", "VAP"]}
plan_generator = Replay(graph, file_name, {**demographic_updaters})

def reward_partial(partition):
    dist_percs = [value/float(partition["VAP"][district]) for district, value in partition["BVAP"].items()]
    num_opport_dists = sum(list(map(lambda v: v >= .5, dist_percs)))
    next_dist = max(i for i in dist_percs if i < .5)
    return num_opport_dists + next_dist

max_score = 0 
max_plan_index = 0
max_cut_edges=0
for i, plan in enumerate(plan_generator):
    score = reward_partial(plan)

    if score >= max_score:
        max_score = score
        max_plan_index = i
        max_cut_edges=len(plan["cut_edges"])

data = [["max_score", "max_score_index","max_cut_edges"],
        [max_score, max_plan_index,max_cut_edges]]


csv_name = (file_name.split(".chain")[0]).split("/")[-1]+".csv"
score_dir = f"{state}_gingles/gingles_scores/{steps}"
directory = Path(score_dir)
directory.mkdir(parents=True, exist_ok=True)

with open(f"{score_dir}/{csv_name}", mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)