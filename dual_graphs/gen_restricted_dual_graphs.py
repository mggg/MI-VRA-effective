# load the dual graph
from gerrychain import Graph
import csv 

mi_vtd_graph = Graph.from_json("mi_vtds_0_indexed_plus_election_indices.json")

# load the VTD to district assignment
vtd_to_house = {}
with open("../Michigan/proposed_plans/vtd_level/state_house/MI-HD-2022_vtd.csv", 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for i, row in enumerate(csv_reader):
        if i>0:
            vtd_to_house[row[0]] = int(row[1])

vtd_to_senate = {}
with open("../Michigan/proposed_plans/vtd_level/state_senate/MI-SD-2022_vtd.csv", 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for i, row in enumerate(csv_reader):
        if i>0:
            vtd_to_senate[row[0]] = int(row[1])

# # create a list of nodes in required districts
house_1_districts = [1,7,8,10,11,12,14,2,3,4,6,9,13]
house_2_districts = [1,7,8,10,11,12,14,2,3,4,5,6,9,13,16]
senate_districts = [1,3,6,8,10,11,2,7]

house_1_nodes = [node for node, data in mi_vtd_graph.nodes(data = True) if vtd_to_house[data["GEOID20"]] in house_1_districts ]
house_2_nodes = [node for node, data in mi_vtd_graph.nodes(data = True) if vtd_to_house[data["GEOID20"]] in house_2_districts ]
senate_nodes = [node for node, data in mi_vtd_graph.nodes(data = True) if vtd_to_senate[data["GEOID20"]] in senate_districts ]


# create a subgraph based on the required districts
house_1_subgraph = Graph.from_networkx(mi_vtd_graph.subgraph(house_1_nodes))
house_2_subgraph = Graph.from_networkx(mi_vtd_graph.subgraph(house_2_nodes))
senate_subgraph = Graph.from_networkx(mi_vtd_graph.subgraph(senate_nodes))

# save the subgraph
house_1_subgraph.to_json("mi_house_1_restricted_vtds.json")
house_2_subgraph.to_json("mi_house_2_restricted_vtds.json")
senate_subgraph.to_json("mi_senate_restricted_vtds.json")
