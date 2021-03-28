from typing import List, Tuple
from itertools import zip_longest
from difflib import SequenceMatcher

# Data class that represents the diff tool
class ProvDiff:

    def __init__()

# Data class for holding provenance graph node information
class ProvNode:

    def __init__(self, name: str, content: str, node_type: str, start_line: int, end_line: int):
        self.name = name
        self.content = content
        self.node_type = node_type
        self.start_line = start_line
        self.end_line = end_line

    def pretty_print(self):
        printed_node = "\n".join([f"Name: {self.name}", f"Content: {self.content}", f"Provenance Type: {self.node_type}"])
        print(printed_node)

class ProvSlice:

    def __init__(self, nodes: List[ProvNode]):
        self._nodes = nodes

    def compute_similarity(self, other_slice: 'ProvSlice') -> float:
        self_content = ''.join([node.content for node in self._nodes]).replace(" ", "")
        other_content = ''.join([node.content for node in other_slice._nodes]).replace(" ", "")
        return SequenceMatcher(None, self_content, other_content).ratio()

    def divergent_nodes(self, other_slice: 'ProvSlice'):
        if len(self._nodes) == len(other_slice._nodes):
            common_len = len(self._nodes)
            zipped_nodes = zip(self._nodes[1:common_len - 1], other_slice._nodes[1:common_len - 1])
            return [(node_a, node_b) for node_a, node_b in zipped_nodes if node_a.content != node_b.content]
        else:
            union = self.slice_union(other_slice)
            cleaned_union = [node for node in union if node.node_type != "Start" and node.node_type != "Finish"]
            content_of_fst = [node.content for node in self._nodes]
            content_of_snd = [node.content for node in other_slice._nodes]
            nodes_not_in_fst = [node for node in cleaned_union if node.content not in content_of_fst]
            nodes_not_in_snd = [node for node in cleaned_union if node.content not in content_of_snd]

    # We do not want duplicate nodes, i.e. nodes with the same program
    # That is why we have this slice_union function
    def slice_union(self, other_slice: 'ProvSlice') -> List[ProvNode]:
        union = { node.content : node for node in self._nodes }
        for node in other_slice._nodes:
            if node.content not in union:
                union[node.content] = node
        return union.values()

    def pretty_print(self):
        for node in self._nodes:
            node.pretty_print()