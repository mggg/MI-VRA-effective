from gerrychain import Partition, MarkovChain, constraints, accept, Election
from gerrychain.updaters import Tally
from gerrychain.tree import recursive_tree_part, bipartition_tree
from gerrychain.proposals import ReCom, recom
from pcompress import Record
from functools import partial
import warnings
from region_aware import *
from vra import vra_metropolis, num_effective_districts


class ChainRecorder:
    def __init__(self, graph, output_dir, pop_col, weight_dict = None, vra_threshold = 0, verbose_freq=None, theta=2, bvap_thresh=.43, biden_thresh=.53) -> None:
        self.graph = graph
        self.output_dir = output_dir
        self.pop_col = pop_col
        self.weight_dict = weight_dict
        self.vra_threshold = vra_threshold
        self.verbose_freq = verbose_freq
        self.theta = theta
        self.bvap_thresh = bvap_thresh
        self.biden_thresh = biden_thresh

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
                        vra_reject = False, vra_climb = False,
                        initial_partition=None):

        valid_initial_partition = False

        while not valid_initial_partition:
            if initial_partition is None:
                initial_partition = self._initial_partition(num_districts, epsilon)

            proposal = self._proposal(num_districts, epsilon)

            # constraints for VRA rejrect
            if not vra_reject:
                cs = [constraints.within_percent_of_ideal_population(initial_partition, epsilon)]

            else:
                cs = [constraints.within_percent_of_ideal_population(initial_partition, epsilon), 
                    constraints.LowerBound(partial(num_effective_districts, bvap_thresh = self.bvap_thresh, biden_thresh = self.biden_thresh), 
                                            self.vra_threshold)]

            # hill climber
            if not vra_climb:
                accept_func = accept.always_accept
            
            elif vra_climb:
                accept_func = partial(vra_metropolis, theta = self.theta, bvap_thresh=self.bvap_thresh, biden_thresh=self.biden_thresh)
            
            try:
                chain = MarkovChain(proposal=proposal, constraints=cs,
                                accept=accept_func, initial_state=initial_partition,
                                total_steps=steps)
                valid_initial_partition = True
            except:
                initial_partition = None

        for i, part in  enumerate(Record(chain, "{}/{}".format(self.output_dir, file_name))):
            if self.verbose_freq is not None and i % self.verbose_freq == self.verbose_freq - 1:
                print("*", end="", flush=True)
