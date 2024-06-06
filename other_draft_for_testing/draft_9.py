import igraph
# import numpy
#
# all_undirected_graph_edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4)]
# all_directed_graph_edges = []
# for one_edge in all_undirected_graph_edges:
#     all_directed_graph_edges.extend([one_edge, tuple(reversed(one_edge))])
# # all_directed_graph_edges = [(one_edge, tuple(reversed(one_edge))) for one_edge in all_undirected_graph_edges]
# print(all_directed_graph_edges)
# test_graph = igraph.Graph(edges=all_directed_graph_edges, directed=True)
# all_cuts_edge_ids = [found_cut.cut for found_cut in test_graph.all_st_cuts(source=0, target=4)]
# all_cuts = []
# for one_edge_group in all_cuts_edge_ids:
#     all_cuts.append([all_directed_graph_edges[one_edge_id] for one_edge_id in one_edge_group])
#
# print(all_cuts_edge_ids)
# print(all_cuts)
# print(test_graph.all_st_cuts(source=0, target=4))

all_directed_graph_edges = []
for one_edge in [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4)]:
    all_directed_graph_edges.extend([one_edge, tuple(reversed(one_edge))])

all_found_cuts = []
for one_edge_group in [found_cut.cut for found_cut in igraph.Graph(edges=all_directed_graph_edges,
                                                                   directed=True).all_st_cuts(source=0, target=4)]:
    all_found_cuts.append([all_directed_graph_edges[one_edge_id] for one_edge_id in one_edge_group])

print(all_found_cuts)

# Error message: 'Plotting not available; please install pycairo or cairocffi'
# igraph.plot(igraph.Graph(edges=all_directed_graph_edges,directed=True))

# test_graph.add_edges([(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4)])

