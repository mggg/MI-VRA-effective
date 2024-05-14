from gerrychain import Graph
import networkx as nx

house_1 = Graph.from_json("mi_house_1_restricted_vtds.json")
house_2 = Graph.from_json("mi_house_2_restricted_vtds.json")
senate = Graph.from_json("mi_senate_restricted_vtds.json")

# preserves node order, just relabels from 0
house_1 = Graph.from_networkx(nx.relabel.convert_node_labels_to_integers(house_1, label_attribute = "old_node_index"))
house_2 = Graph.from_networkx(nx.relabel.convert_node_labels_to_integers(house_2, label_attribute = "old_node_index"))
senate = Graph.from_networkx(nx.relabel.convert_node_labels_to_integers(senate, label_attribute = "old_node_index"))

house_1.to_json("mi_house_1_restricted_vtds_0_indexed.json")
house_2.to_json("mi_house_2_restricted_vtds_0_indexed.json")
senate.to_json("mi_senate_restricted_vtds_0_indexed.json")