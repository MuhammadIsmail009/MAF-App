from pathlib import Path
from typing import Any, Dict


def run_volatility_plugins(dump_path: Path) -> Dict[str, Any]:
    """
    Wrapper around Volatility 3.

    In a production deployment this should import and run real Volatility3
    plugins (pslist, pstree, malfind, dlllist, handles, netscan, cmdline)
    and normalize their output to JSON.

    For environments without volatility3 installed or when analysis fails,
    this function should raise a RuntimeError or return a best-effort,
    clearly-marked partial result.
    """
    # TODO: integrate real volatility3. For now, we return a mocked structure
    # so that the rest of the pipeline works end-to-end.
    # This minimal data is enough to drive the ML/dashboards.
    processes = [
        {
            "pid": 4,
            "ppid": 0,
            "name": "System",
            "threads": 80,
            "dll_count": 120,
            "entropy": 0.3,
            "suspicious": False,
            "connections": [],
        },
        {
            "pid": 5324,
            "ppid": 712,
            "name": "svch0st.exe",
            "threads": 12,
            "dll_count": 30,
            "entropy": 0.92,
            "suspicious": True,
            "connections": [
                {"remote_ip": "185.23.1.10", "remote_port": 4444, "protocol": "TCP"},
            ],
        },
    ]

    netscan = [c for p in processes for c in p.get("connections", [])]

    return {
        "pslist": processes,
        "pstree": processes,  # simplified for now
        "malfind": [],
        "dlllist": [],
        "handles": [],
        "netscan": netscan,
        "cmdline": [],
        "source": "mock",
    }



