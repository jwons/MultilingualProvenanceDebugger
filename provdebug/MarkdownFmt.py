from typing import Dict
from .DebugTrace import DebugTrace
from .DebugRecord import DebugRecord

class MarkdownFmt:
    
    def metadata_str(self, metadata: Dict[str, str]) -> str:
        header = "# Debugging Trace"
        os_str = f' * {metadata["os"]}'
        python_ver_str = f'* {metadata["python-version"]}'
        return "\n".join([header, os_str, python_ver_str])

    def trace_str(self, debug_trace: DebugTrace) -> str:
        records = debug_trace._debug_records
        trace = [self._record_str(i, record) for i, record in enumerate(records)]
        return "\n".join(trace)

    def _record_str(self, record_index: int, record: DebugRecord) -> str:
        # adding 1 to record_index to account for 0-based indexing
        header = f"## Step {record_index + 1}"
        action_str = f"**Debug action**: {record._userChoice}"
        program_state_str = f"**Program state**:\n```\n{record._programInfo}\n```"
        record_strs = [header, action_str, program_state_str]
        if record._userAnnotation is not None:
            annotation_str = f"**Annotation**: {record._userAnnotation}"
            record_strs.append(annotation_str)
        return "\n".join(record_strs)
