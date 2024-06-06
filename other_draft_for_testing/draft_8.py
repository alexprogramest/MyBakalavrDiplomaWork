# from networkx.algorithms.connectivity import minimum_st_edge_cut

import networkx as nx

test_graph = nx.Graph()
test_graph.add_edges_from([(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4)])

all_cuts = []

for n in test_graph.nodes:
    for k in test_graph.nodes:
        if n == k:
            continue
        all_cuts.append(nx.algorithms.connectivity.minimum_st_edge_cut(test_graph, n, k))

all_min_cuts = [frozenset([tuple(sorted(i)) for i in j]) for j in
                [frozenset(cut) for cut in all_cuts if len(cut) == len(min(all_cuts, key=len))]]
all_min_cuts = [set(s) for s in set(all_min_cuts)]
print(all_min_cuts)
