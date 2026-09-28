"""Session 45: reproduces firstorder_window_s45_b16.json = the session-44 first-order window prediction with B = 256, 64 AND 16
(numpy on split files only). Runs firstorder_window_s44.main() with BS = (256, 64, 16) and restores the s44 json afterwards;
the iid-dependent fields differ from s44 only in the 4th decimal (random permutations).
  python lab/experiments/EXP-100-set-vs-order/firstorder_window_s45_b16.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import firstorder_window_s44 as f  # noqa: E402

S44, S45 = HERE / "firstorder_window_s44.json", HERE / "firstorder_window_s45_b16.json"


def main() -> None:
    keep = S44.read_bytes()
    try:
        f.BS = (256, 64, 16)
        f.main()
        S45.write_bytes(S44.read_bytes())
    finally:
        S44.write_bytes(keep)


if __name__ == "__main__":
    main()
