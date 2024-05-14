from plan_metrics import PlanMetrics
from gerrychain import Graph, Election, Partition
from gerrychain.updaters import Tally
from pcompress import Replay
import argparse
import json
import gzip
import warnings
from configuration import *
from vra import num_effective_districts
import pandas as pd

SUPPORTED_METRIC_IDS = list(SUPPORTED_METRICS.keys())

parser = argparse.ArgumentParser(description="VTD Ensemble Scorer", 
                                 prog="collect_scores_embed_partial.py")


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

args = parser.parse_args()

## Read in args and state specifications
state = "Michigan_restricted"
partial_plan_type = args.map

if "house" in partial_plan_type:
    full_plan_type = "state_house"
else:
    full_plan_type = "state_senate"

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
    raise ValueError("Cannot run vra aware and climb concurrently.")

elif vra_reject:
    vra_string = "reject"

elif vra_climb:
    vra_string = "climb"

else:
    vra_string = "neutral"


# all of these stats are about the full state
with open("{}/{}.json".format(STATE_SPECS_DIR, "Michigan")) as fin:
    state_specification = json.load(fin)

k = state_specification["districts"][full_plan_type]
eps = state_specification["epsilons"][full_plan_type]
dual_graph_file = "{}/{}".format(DUAL_GRAPH_DIR, state_specification["dual_graph"][full_plan_type])
pop_col = state_specification["pop_col"]
county_col = state_specification["county_col"]
party = state_specification["pov_party"]
elections = state_specification["elections"]
election_names = [e["name"] for e in elections]
demographic_cols = [m["id"] for m in state_specification["metrics"] if "type" in m and m["type"] == "col_tally"]
state_metric_ids = set([m["id"] for m in state_specification["metrics"] if "type" not in m or m["type"] != "col_tally"])
state_metrics = [{**m, "type": SUPPORTED_METRICS["col_tally"]} if ("type" in m and m["type"] == "col_tally") \
                                                               else {**m, "type": SUPPORTED_METRICS[m["id"]]} \
                    for m in filter(lambda m: m["id"] in SUPPORTED_METRIC_IDS or ("type" in m and m["type"] == "col_tally"), 
                                    state_specification["metrics"])]
municipality_col = state_specification["municipal_col"] if "num_municipal_pieces" in state_metric_ids or "num_split_municipalities" in state_metric_ids else None
incumbent_col = state_specification["incumbent_cols"][full_plan_type] if "num_double_bunked" in state_metric_ids or "num_zero_bunked" in state_metric_ids else None

full_dual_graph = Graph.from_json(dual_graph_file)

with open("{}/{}.json".format(STATE_SPECS_DIR, "Michigan_restricted")) as fin:
    state_specification = json.load(fin)
partial_dual_graph_file = "{}/{}".format(DUAL_GRAPH_DIR, state_specification["dual_graph"][partial_plan_type])
partial_dual_graph = Graph.from_json(partial_dual_graph_file)

if len(state_metric_ids - set(SUPPORTED_METRIC_IDS)) > 0:
    warnings.warn("Some state metrics are not supported.  Will continue without tracking them.\n.\
                  Unsupported metrics: {}".format(str(state_metric_ids - set(SUPPORTED_METRIC_IDS))))


## sort candidates alphabetically so that the "first" party is consistent.
election_updaters = {e["name"]: Election(e["name"], {c["name"]: c["key"] for c in sorted(e["candidates"], 
                                                                                         key=lambda c: c["name"])})
                    for e in elections}
demographic_updaters = {demo_col: Tally(demo_col, alias=demo_col) for demo_col in demographic_cols + [incumbent_col]}



scores = PlanMetrics(full_dual_graph, election_names, party, pop_col, state_metrics, updaters=election_updaters, 
                     county_col=county_col, demographic_cols=demographic_cols,
                     municipality_col=municipality_col, incumbent_col=incumbent_col)

# since we are embedding into full state, always use partial chain
chain_path = f"Michigan_restricted/{CHAIN_DIR}/michigan_restricted_{partial_plan_type}_{eps}_bal_{steps}_steps_{region_aware_str}_vra_{vra_string}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}.chain"
output_path = f"Michigan_embed/{STATS_DIR}/michigan_embed_{partial_plan_type}_{eps}_bal_{steps}_steps_{region_aware_str}_vra_{vra_string}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}.jsonl.gz"

if full_plan_type == "congress":
    file_name = "MI-CD-2022_vtd.csv"
elif full_plan_type == "state_house":
    file_name = "MI-HD-2022_vtd.csv"
elif full_plan_type == "state_senate":
    file_name = "MI-SD-2022_vtd.csv"

plan = pd.read_csv(f"Michigan/proposed_plans/vtd_level/{full_plan_type}/{file_name}", dtype={"GEOID20": "str", "assignment": int}).set_index("GEOID20").to_dict()['assignment']
full_assignment_vector = {n: plan[full_dual_graph.nodes()[n]["GEOID20"]] for n in full_dual_graph.nodes()}

partial_geoids = [data["GEOID20"]for n, data in partial_dual_graph.nodes(data=True)]
fixed_nodes = [n for n,data in full_dual_graph.nodes(data=True) if data["GEOID20"] not in partial_geoids]
fixed_assignment_vector = {n:full_assignment_vector[n] for n in fixed_nodes}

print("about to score")

with gzip.open(output_path, "wt") as fout:
    plan_generator = Replay(partial_dual_graph, chain_path, {**demographic_updaters, **election_updaters})
    
    
    part = Partition(full_dual_graph, full_assignment_vector, {**demographic_updaters, **election_updaters})


    # prints header and summary of scores
    header = json.dumps(scores.summary_data(elections, districts=part.parts.keys(), epsilon=eps, method=region_aware_str+vra_string)) + "\n"
    plan_details = json.dumps(scores.plan_summary(part, bvap_thresh, biden_thresh)) + "\n"
    fout.write(header)
    fout.write(plan_details)



    for i, part in enumerate(plan_generator):
        # reindexes partial assignment vector to fit back into main dual graph
        # +300 allows you to avoid issues of indexing for districts
        partial_assignment ={partial_dual_graph.nodes[n]["old_node_index"]:d+300 for n,d in part.assignment.items()}
        new_full_assignment = {**partial_assignment, **fixed_assignment_vector}
        full_partition = Partition(full_dual_graph, new_full_assignment, {**demographic_updaters, **election_updaters})

        
        plan_details = json.dumps(scores.plan_summary(full_partition, bvap_thresh, biden_thresh)) + "\n"
        fout.write(plan_details)

        # # TODO for testing
        # if i > 2:
        #     print("done testing")
        #     break

# # TODO testing
# method = f"{region_aware_str}_vra_{vra_string}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}"
# print(f"Michigan_embed/ensemble_stats/michigan_embed_{partial_plan_type}_{eps}_bal_{steps}_steps_{method}.jsonl.gz")
# with gzip.open(f"Michigan_embed/ensemble_stats/michigan_embed_{partial_plan_type}_{eps}_bal_{steps}_steps_{method}.jsonl.gz", "rb") as fe:
#     ensemble_list = list(fe)
#     ensemble_summary = json.loads(ensemble_list[0])
#     ensemble_plans = [json.loads(j) for j in ensemble_list if json.loads(j)["type"] == "ensemble_plan"]

# plan = ensemble_plans[-1]
# print(len(plan["TOTPOP"].keys()))
