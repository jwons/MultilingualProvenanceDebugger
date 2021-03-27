from .ProvGrapher import Grapher
import networkx as nx

class ProvDiffer:

    def __init__(self, fst_graph: Grapher, snd_graph):
        self._fst_graph = fst_graph._graph
        self._snd_graph = snd_graph._graph
    
    def is_isomorphic(self) -> bool:
        return nx.is_isomorphic(self._fst_graph, self._snd_graph)

    def yield_mapping(self):
        return nx.algorithms.isomorphism.GraphMatcher(self._fst_graph, self._snd_graph).match()
    
    def difference(self):
        fst_diff_snd = nx.difference(self._fst_graph, self._snd_graph)
        print(fst_diff_snd)
        snd_diff_fst = nx.difference(self._snd_graph, self._fst_graph)
        print(snd_diff_fst)
        return nx.union(fst_diff_snd, snd_diff_fst)