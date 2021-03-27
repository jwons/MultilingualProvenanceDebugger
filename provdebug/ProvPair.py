from typing import List, Tuple
from difflib import SequenceMatcher

class ProvPair:

    def __init__(self, pairs: List[Tuple[str, str]]):
        self._pairs = pairs

    def compute_similarity(self, mapping: 'ProvMap') -> float:
        self_content = ''.join([v for _, v in self._pairs])
        other_content = ''.join([v for _, v in mapping._pairs]) 
        return SequenceMatcher(None, self_content, other_content).ratio()

    def pretty_print(self):
        for k, v in self._mapping:
            print(f"{k} --> {v}")