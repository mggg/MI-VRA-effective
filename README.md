# MI-VRA-effective
Replication repository for "Balancing Partisanship and Voting Rights Law in Michigan Legislative Maps".


# General Outline  
- construct dual graphs and store in `dual_graphs`. Update `state_specifications` json files with dual graph name.
- Add proposed plans as vtd to district csv files to `Michigan/proposed_plans` subdirectory. In `Michigan_restricted/proposed_plans`, restrict any plans with `restrict_a_plan.py.` Helper scripts for block to vtd conversion in `dual_graphs`.
- Generate ensembles with `*_state_scripts` kick off/start sentinel code. Score ensembles with `kick_off_figures.sh`. Generate figures with various figure scripts.

# Directories
## dual_graphs
Contains dual graphs used for project, along with several scripts used in their creation. `mi_vtds_0_indexed_w_elections.json` was the original bespoke dual graph.
- `block_to_vtd_mapping.py` creates a vtd assignment csv from a block assignment csv.
- `gen_restricted_dual_graphs.py` creates a subgraph for partial scrambles.
- `reindex_dual_graphs.py` reindexes dual graphs using integer labels so that `pcompress` can reload files properly.

## Figures
Directory for saving figures.

## full_state_scripts
Scripts for full state ensembles to be run on cluster. In order of use:
- `start_sentinel.sh` begins Recom ensembles. Parameters for runs can be changed in `submit_batch_chain.sh`. Saves chains to `Michigan/raw_chains`.
- `kick_off_state_scoring.sh` scores the saved chains.
- `start_sentinel_figures.sh` begins figure generation. Parameters for runs can be changed in `submit_batch_figures.sh`.

## gingles_scripts
Used for Gingles 1 prong, optimizing for majority BVAP. In order of use:
- `start_sentinel_chain.sh` begins Recom optimization ensembles. Parameters for runs can be changed in `submit_batch_chain.sh`. Saves chains to `Michigan_gingles/raw_chains`.
- `start_sentinel_chain_anneal.sh` begins Recom simulated anneal ensembles. Parameters for runs can be changed in `submit_batch_chain_anneal.sh`. Saves chains to `Michigan_gingles/raw_chains`.
- `start_sentinel_score.sh` begins scoring raw chains. Parameters for runs can be changed in `submit_batch_score.sh`.
- `gingles_df.ipynb` sorts the scored ensembles and finds the optimized maps. Plots them.

## Michigan
Contains raw chains, scored chains, and proposed plans for full state level.

## Michigan_embed
Contains scored chains for partial scrambles embedded back into full state.

## Michigan_restricted
Contains raw chains, scored chains, and proposed plans for partial scrambles.
- `proposed_plans/restrict_a_plan.py` restricts a proposed plan to the partial scramble.

## restricted_state_scripts
Scripts for partial state ensembles to be run on cluster. In order of use:
- `start_sentinel_chain.sh` begins Recom ensembles. Parameters for runs can be changed in `submit_batch_chain.sh`. Saves chains to `Michigan_restricted/raw_chains`.
- `start_sentinel_score.sh` begins scoring ensembles. Parameters for runs can be changed in `submit_batch_score.sh`. Saves chains to `Michigan_restricted/ensemble_stats`.
- `start_sentinel_figures.sh` begins figure generation. Parameters for runs can be changed in `submit_batch_figures.sh`.

## shapefiles
Shapefiles for proposed plans and MI VTDs. 
- `proposed_plans_maup_to_vtd.py` creates VTD assignments of proposed plans and stores them in `Michigan/proposed_plans/vtd_level`.

## state_specificiations
json files describing various constants for each level of analysis, like number of districts, plan names, etc.

## Tables
Directory for storing various tables generated for paper.

## Top level files
- `collect_*` these files score the various raw chains.
- `configuration.py` various directory and score settings.
- `ensemble_paths.json` dummy file needed due to `plotting_class.py`.
- `ensemble_stats_table.*` used to create table for paper containing general stats about the ensembles, like county splits and VRA districts,
- `kick_off_*` all begin different figure generations. `figures` is basic histograms, `num_effective_figs` winnows the histograms by VRA district count, and `scatterplots*` create scatterplots of VRA vs. stat.
- `MI_by_num_effective_figs.py` script called by `MI_num_effective_figs.sh`.
- `MI_figures.sh` script called by `kick_off_figures.sh`.
- `MI_num_effective_figs.sh` script called by `kick_off_num_effective_figs.sh`.
- `MI_plots*` scripts called by figure bash scripts.
- `MI_scatter*` scripts called by scatter kickoff bash scripts.
- `partisan_scores.py` updaters for partisan scores not in gerrychain.
- `plan_metrics.py` class for scoring chains.
- `plotting_class.py` class for plotting figures.
- `plotting_configuration.py` plotting configuration defaults.
- `proposed_plans_table.py` generates table of stats about proposed plans.
- `record_chains*` classes for recording raw chains.
- `run_ensemble*` scripts called to generate ensembles.
- `score_gingles.py` collects scores from Gingles ensembles.
- `score_non_recom_plans*` collects scores for benchmark maps and stores them in `plan_stats` subfolders.
- `setup.py` setup config.
- `vra_and_eg_table.*` generate table about ensemble beating score thresholds.
- `vra.py` VRA district functions.
