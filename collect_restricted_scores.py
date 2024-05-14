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
                                 prog="collect_restricted_scores.py")

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
parser.add_argument('--verbose', '-v', action='count', default=0)
parser.add_argument("--sub_sample", metavar="stride length", default=1, type=int, 
                    help="Stride length for sub-sampling the plan. Default is not to sub-sample.")
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
    raise ValueError("Cannot run vra aware and climb concurrently.")

elif vra_reject:
    vra_string = "reject"

elif vra_climb:
    vra_string = "climb"

else:
    vra_string = "neutral"
how_verbose = args.verbose
stride_len = args.sub_sample

with open("{}/{}.json".format(STATE_SPECS_DIR, state)) as fin:
    state_specification = json.load(fin)

k = state_specification["districts"][plan_type]
eps = state_specification["epsilons"][plan_type]
dual_graph_file = "{}/{}".format(DUAL_GRAPH_DIR, state_specification["dual_graph"][plan_type])
pop_col = state_specification["pop_col"]
county_col = state_specification["county_col"]
party = state_specification["pov_party"]
elections = state_specification["elections"]
demographic_cols = [m["id"] for m in state_specification["metrics"] if "type" in m and m["type"] == "col_tally"]
state_metric_ids = set([m["id"] for m in state_specification["metrics"] if "type" not in m or m["type"] != "col_tally"])
state_metrics = [{**m, "type": SUPPORTED_METRICS["col_tally"]} if ("type" in m and m["type"] == "col_tally") \
                                                               else {**m, "type": SUPPORTED_METRICS[m["id"]]} \
                    for m in filter(lambda m: m["id"] in SUPPORTED_METRIC_IDS or ("type" in m and m["type"] == "col_tally"), 
                                    state_specification["metrics"])]
municipality_col = state_specification["municipal_col"] if "num_municipal_pieces" in state_metric_ids or "num_split_municipalities" in state_metric_ids else None
incumbent_col = state_specification["incumbent_cols"][plan_type] if "num_double_bunked" in state_metric_ids or "num_zero_bunked" in state_metric_ids else None

graph = Graph.from_json(dual_graph_file)
# VRA rejection threshold will be computed based on enacted map
file_name = f"{plan_type}_vtd.csv"
plan = pd.read_csv(f"Michigan_restricted/proposed_plans/vtd_level/{plan_type}/{file_name}", dtype={"GEOID20": "str", "assignment": int}).set_index("GEOID20").to_dict()['assignment']
ddict = {n: plan[graph.nodes()[n]["GEOID20"]] for n in graph.nodes()}

updaters  = {"population": Tally(pop_col, alias="population"),
                            "PRES20": Election("PRES20", {"Democratic": "G20PREDBID", "Republican": "G20PRERTRU"}),
                            "BVAP": Tally("BVAP", alias="BVAP"),
                            "VAP": Tally("VAP", alias="VAP")}

part = Partition(graph, ddict, updaters)
vra_threshold = num_effective_districts(part, bvap_thresh, biden_thresh)

cousub_col = state_specification["municipal_col"]
weight_dict = {county_col: county_weight, cousub_col:county_sub_weight}



if len(state_metric_ids - set(SUPPORTED_METRIC_IDS)) > 0:
    warnings.warn("Some state metrics are not supported.  Will continue without tracking them.\n.\
                  Unsupported metrics: {}".format(str(state_metric_ids - set(SUPPORTED_METRIC_IDS))))

# path_long = "mi_chains/mi_cong_0.01_bal_10000_steps_non_county_aware.chain"
chain_path = f"{state}/{CHAIN_DIR}/{state.lower()}_{plan_type}_{eps}_bal_{steps}_steps_{region_aware_str}_vra_{vra_string}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}.chain"
output_path = f"{state}/{STATS_DIR}/{state.lower()}_{plan_type}_{eps}_bal_{steps}_steps_{region_aware_str}_vra_{vra_string}_theta_{theta}_bvap_{bvap_thresh}_biden_{biden_thresh}.jsonl.gz"

election_names = [e["name"] for e in elections]
## sort candidates alphabetically so that the "first" party is consistent.
election_updaters = {e["name"]: Election(e["name"], {c["name"]: c["key"] for c in sorted(e["candidates"], 
                                                                                         key=lambda c: c["name"])})
                    for e in elections}
demographic_updaters = {demo_col: Tally(demo_col, alias=demo_col) for demo_col in demographic_cols + [incumbent_col]}



scores = PlanMetrics(graph, election_names, party, pop_col, state_metrics, updaters=election_updaters, 
                     county_col=county_col, demographic_cols=demographic_cols,
                     municipality_col=municipality_col, incumbent_col=incumbent_col)


print("about to score")
with gzip.open(output_path, "wt") as fout:
    plan_generator = Replay(graph, chain_path, {**demographic_updaters, **election_updaters})
    part = next(plan_generator)

    # TODO what is method exactly?
    header = json.dumps(scores.summary_data(elections, districts=part.parts.keys(), epsilon=eps, method=region_aware_str+vra_string)) + "\n"
    plan_details = json.dumps(scores.plan_summary(part, bvap_thresh, biden_thresh)) + "\n"
    fout.write(header)
    fout.write(plan_details)

    if how_verbose >= 2:
        for i, part in enumerate(plan_generator):
            if i % stride_len == stride_len - 1:
                plan_details = json.dumps(scores.plan_summary(part, bvap_thresh, biden_thresh)) + "\n"
                fout.write(plan_details)
    else:
        for i, part in enumerate(plan_generator):
            if i % stride_len == stride_len - 1:
                if how_verbose > 0 and i % 100 == 100 - 1:
                    print("*", end="", flush=True)
                plan_details = json.dumps(scores.plan_summary(part, bvap_thresh, biden_thresh)) + "\n"
                fout.write(plan_details)

print("done")
