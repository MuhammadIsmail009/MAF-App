from typing import Any, Dict, List

import pandas as pd


def processes_to_dataframe(processes: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for p in processes:
        rows.append(
            {
                "pid": p.get("pid"),
                "ppid": p.get("ppid"),
                "name": p.get("name"),
                "threads": p.get("threads", 0),
                "dll_count": p.get("dll_count", 0),
                "entropy": p.get("entropy", 0.0),
                "suspicious_flag": 1 if p.get("suspicious") else 0,
                "net_conn_count": len(p.get("connections", [])),
            }
        )
    return pd.DataFrame(rows)



