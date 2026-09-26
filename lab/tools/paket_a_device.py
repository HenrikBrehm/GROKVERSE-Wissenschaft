"""Device of the programme-A runs (session 15; fallback if GPU-001 fails). UNTESTED.

LAB_PAKET_A_DEVICE = "cuda" (default, unchanged behaviour) or "cpu". Rule 16d: all arms and seeds of one experiment on one device; the
analyses read only the runs of this device (freq_ban adds "_devcuda" to GPU run ids and nothing on the CPU; the EXP-046/048/049 trainers
always add "_dev<device>"). Set by `night_program.py --paket-a-cpu` for its jobs; set it yourself when running an analysis by hand.
"""
from __future__ import annotations

import os

DEV = os.environ.get("LAB_PAKET_A_DEVICE", "cuda")
if DEV not in ("cuda", "cpu"):
    raise SystemExit(f"LAB_PAKET_A_DEVICE must be 'cuda' or 'cpu', not {DEV!r}")
FB_SUFFIX = "_devcuda" if DEV == "cuda" else ""     # freq_ban run ids
TR_SUFFIX = f"_dev{DEV}"                              # group_train / intadd_train / width_train run ids
