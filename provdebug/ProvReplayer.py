import json
from .DebugRecord import DebugRecord

class Replayer:

    def __init__(self, filename):
        f = open(filename, "r")
        raw_file_content = f.read()
        file_content_json = json.loads(raw_file_content)
        debug_records = [DebugRecord.fromDict(d) for d in file_content_json]
        pass