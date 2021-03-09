from .DebugRecord import DebugRecord
from typing import Optional, List, Dict

class DebugTrace:

    def __init__(self, debug_records: List[DebugRecord], debug_metadata: Dict[str, str]):
        self._record_index = 0
        self._debug_records = debug_records
        self._debug_metadata = debug_metadata

    def pretty_print_metadata(self):
        operating_sys = self._debug_metadata["os"]
        python_ver = self._debug_metadata["python-version"]
        print(f"Operating system: {operating_sys}\nPython version: {python_ver}")

    def current_record(self) -> DebugRecord:
        return self._debug_records[self._record_index]

    def prev_record(self) -> Optional[DebugRecord]:
        if self._record_index - 1 >= 0:
            self._record_index -= 1
            return self._debug_records[self._record_index]
        return None

    def next_record(self) -> Optional[DebugRecord]:
        if self._record_index + 1 < len(self._debug_records):
            self._record_index += 1
            return self._debug_records[self._record_index]
        return None

    def is_empty_trace(self):
        return len(self._debug_records) == 0

