import json
from .DebugRecord import DebugRecord
from .DebugTrace import DebugTrace
class Replayer:

    def __init__(self, filename):
        f = open(filename, "r")
        raw_file_content = f.read()
        replay_json = json.loads(raw_file_content)
        records = replay_json["records"]
        self._debug_records = [DebugRecord.fromDict(d) for d in records]
        self._debug_metadata = replay_json["metadata"]
    
    def getDebugRecords(self):
        return self._debug_records

    def getDebugTrace(self):
        return DebugTrace(self._debug_records, self._debug_metadata)