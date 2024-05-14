from gerrychain import Partition, MarkovChain, constraints, accept, Election
from gerrychain.updaters import Tally
from gerrychain.tree import recursive_tree_part, bipartition_tree
from gerrychain.proposals import ReCom, recom
from gerrychain.optimization import SingleMetricOptimizer, Gingleator
from pcompress import Record
from functools import partial
import warnings
from region_aware import *
from vra import vra_metropolis, num_effective_districts


class ChainRecorder:
    def __init__(self, graph, output_dir, pop_col, weight_dict = None) -> None:
        self.graph = graph
        self.output_dir = output_dir
        self.pop_col = pop_col
        self.weight_dict = weight_dict

        ## Set up pop info
        self.tot_pop = sum([graph.nodes()[n][pop_col] for n in graph.nodes()])
        self.updaters = {"population": Tally(pop_col, alias="population"),
                            "PRES20": Election("PRES20", {"Democratic": "G20PREDBID", "Republican": "G20PRERTRU"}),
                            "BVAP": Tally("BVAP", alias="BVAP"),
                            "VAP": Tally("VAP", alias="VAP")}

    def _initial_partition(self, num_districts, epsilon):
        ideal_pop = self.tot_pop / num_districts
        method = partial(bipartition_tree, allow_pair_reselection=True)
        cddict = recursive_tree_part(self.graph, range(num_districts), ideal_pop, self.pop_col,
                                     epsilon, method = method)
        part = Partition(self.graph, assignment=cddict, updaters=self.updaters)
        return part

    def _proposal(self, num_districts, epsilon):
        ideal_pop = self.tot_pop / num_districts
        method = partial(bipartition_tree, allow_pair_reselection=True)
        return partial(recom, pop_col = self.pop_col, pop_target = ideal_pop,
                        epsilon = epsilon, region_surcharge = self.weight_dict,
                        method = method)

    def get_partition(self, ddict):
        part = Partition(self.graph, assignment=ddict, updaters=self.updaters)
        return part

    def record_chain(self, num_districts, epsilon, steps, file_name,  
                        tilt_prob=0, burst_length = 0,
                        initial_partition=None, hot = 0, cold = 0, beta_magnitude = 0):

        valid_initial_partition = False

        while not valid_initial_partition:
            if initial_partition is None:
                initial_partition = self._initial_partition(num_districts, epsilon)
                print("ip generated")

            proposal = self._proposal(num_districts, epsilon)

            # constraints
            cs = [constraints.within_percent_of_ideal_population(initial_partition, epsilon)]
            
            try:
                chain = MarkovChain(proposal=proposal, constraints=cs,
                                accept=accept.always_accept, initial_state=initial_partition,
                                total_steps=steps)
                valid_initial_partition = True
                print("initial partition valid")
            except:
                print("ip failed")
                initial_partition = None
            
        # will optimize for districts over 50% BVAP
        gingles = Gingleator(proposal, cs, initial_partition, 
                    minority_pop_col="BVAP", total_pop_col="VAP",
                    score_function=Gingleator.reward_partial_dist)

        if not hot and not cold and not beta_magnitude:
            # tilt
            if tilt_prob and not burst_length:
                chain = gingles.tilted_run(num_steps = steps, 
                                            p = tilt_prob)
            # short burst
            elif not tilt_prob and burst_length:
                chain = gingles.short_bursts(burst_length = burst_length, 
                                            num_bursts = int(steps / burst_length))
            
            # variable length short burst
            elif not tilt_prob and not burst_length:
                chain = gingles.variable_length_short_bursts(num_steps = steps, stuck_buffer = 10)
            
            # tilted short burst
            else:
                chain = gingles.tilted_short_bursts(burst_length = burst_length, 
                                            num_bursts = int(steps / burst_length), 
                                            p = tilt_prob)
        
        elif hot and cold and beta_magnitude:
            chain = gingles.simulated_annealing(steps, gingles.jumpcycle_beta_function(hot, cold),
                                                     beta_magnitude=beta_magnitude)
        
        else:
            raise ValueError("all of hot, cold, and beta_magnitude must be non-zero or zero")

        for i, part in enumerate(Record(chain, f"{self.output_dir}/{file_name}")):
            if i%1000 == 0:
                print("*", end="", flush=True)
        print("\n")
        print(f"The best score found was {gingles.best_score}")

        
