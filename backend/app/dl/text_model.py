from typing import Any, Dict, List

import numpy as np


def analyze_strings(strings: List[str]) -> Dict[str, Any]:
    """
    Placeholder for a BERT/LSTM-based text-analysis model.

    For now we compute a simple heuristic score based on the presence of
    suspicious keywords that often show up in malware or C2 traffic.
    """
    if not strings:
        return {"dl_score": 0.0, "details": []}

    keywords = ["mimikatz", "powershell", "invoke", "encode", "shellcode", "payload"]
    scores = []
    details = []

    for s in strings:
        lower = s.lower()
        hits = [k for k in keywords if k in lower]
        score = min(1.0, len(hits) * 0.25)
        scores.append(score)
        details.append({"text": s[:200], "score": score, "keywords": hits})

    avg_score = float(np.mean(scores))
    return {"dl_score": avg_score, "details": details}



