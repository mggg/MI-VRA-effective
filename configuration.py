## Constants
SUPPORTED_STATES = ["Michigan", "Michigan_restricted", "Michigan_embed"]
SUPPORTED_PLAN_TYPES = ["congress", "state_senate", "state_house", "house_1", "house_2", "senate"]

DUAL_GRAPH_DIR = "dual_graphs"
STATE_SPECS_DIR = "state_specifications"
CHAIN_DIR = "raw_chains"
STATS_DIR = "ensemble_stats"

SUPPORTED_METRICS = {
    "col_tally": "district_level",
    "num_cut_edges": "plan_wide",
    "avg_polsby_popper": "plan_wide",
    "avg_reock": "plan_wide",
    "num_county_pieces": "plan_wide",
    "num_split_counties": "plan_wide",
    "num_municipal_pieces": "plan_wide",
    "num_split_municipalities": "plan_wide",
    "num_traversals": "plan_wide",
    "seats": "election_level",
    "efficiency_gap": "election_level",
    "mean_median": "election_level",
    "partisan_bias": "election_level",
    "eguia_county": "election_level",
    "num_swing_districts": "plan_wide",
    "num_competitive_districts": "plan_wide",
    "num_party_districts": "plan_wide",
    "num_op_party_districts": "plan_wide",
    "num_party_wins_by_district": "plan_wide",
    "num_double_bunked": "plan_wide",
    "num_zero_bunked": "plan_wide",
    "num_vra_effective": "plan_wide",
    "avg_efficiency_gap": "plan_wide",
    "avg_s_efficiency_gap": "plan_wide",
    "avg_lopsided_margin": "plan_wide",
    "avg_mean_median" : "plan_wide",
    "s_efficiency_gap": "election_level",
    "lopsided_margin": "election_level",
    "mean_disprop": "plan_wide",
    "num_d_seats_pres_16": "plan_wide",
    "num_maj_bvap_dist": "plan_wide",
    "disprop": "election_level"
}

SUPPORTED_MAP_TYPES = ["ensemble_plan", "citizen_plan", "proposed_plan"]
