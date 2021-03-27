from typing import List, Tuple
from itertools import zip_longest
from difflib import SequenceMatcher

class ProvPair:

    def __init__(self, pairs: List[Tuple[str, str]]):
        self._pairs = pairs

    def compute_similarity(self, mapping: 'ProvPair') -> float:
        self_content = ''.join([v for _, v in self._pairs]).replace(" ", "")
        other_content = ''.join([v for _, v in mapping._pairs]).replace(" ", "")
        return SequenceMatcher(None, self_content, other_content).ratio()

    def divergent_slices(self, mapping: 'ProvPair'):
        divergent = []
        longest = range(max(len(self._pairs), len(mapping._pairs)))
        default = "n/a"
        zipped = list(zip_longest(self._pairs, mapping._pairs, longest, fillvalue=default))
        # TODO: which version of the program do we store to present to the user?
        pass

    def pretty_print(self):
        for k, v in self._pairs:
            print(f"{k} --> {v}")