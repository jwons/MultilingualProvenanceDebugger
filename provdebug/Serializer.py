import platform
import json
import random
from .DebugRecord import DebugRecord
from typing import List, Dict

class Serializer:

    @staticmethod
    def save_records(records: List[DebugRecord], filename):
        record_dicts = [r.writeDict() for r in records]
        metadata = Serializer.platform_metadata()
        replay_dict = {} 
        replay_dict["metadata"] = metadata
        replay_dict["records"] = record_dicts
        replay_file = json.dumps(replay_dict)
        f = open(f"./{filename}.replay", "w")
        f.write(replay_file)
        f.close()

    @staticmethod
    def platform_metadata() -> Dict[str, str]:
        metadata = {}
        metadata["os"] = platform.platform()
        metadata["python-version"] = platform.python_version()
        return metadata

