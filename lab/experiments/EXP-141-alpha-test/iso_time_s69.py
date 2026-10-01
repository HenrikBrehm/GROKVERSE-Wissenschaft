"""EXP-141 amendment a (session 69, written before 10 of the 12 EXP-141 runs finished): iso-time exponent.

The threshold question (does a cell generalize within 30 000 steps?) is coarse; the median generalization step g is
continuous. Descriptive question: how does the number of pairs N_T(p) needed for median g = T scale with p?
N_T ~ p^alpha_T. alpha_T is NOT the threshold alpha of EXP-139 amendment b (that one is about 'ever within budget').

Fixed procedure (constructed F/G arms of EXP-137/139/141, full batch, 30 000-step budget):
1. Cell median g over all 6 arms (seeds x F/G); a non-generalized arm counts as > 30 000; the median is defined only
   if >= 4 of 6 arms generalized.
2. Local slope s = mean over p in {211, 307} of dlog g / dlog N between the two smallest generalizing cells.
3. N_T(p): log-interpolation between two cells with defined medians if available, else from one cell with slope s
   (the cell closest to T in log g).
4. Prediction (before the remaining EXP-141 runs): fit log N_T = a + alpha_T log p over p in {211, 307, 401};
   predicted median g at 503/16 100 and 503/18 100 = T (N / N_T(503))^s.
5. Reading after EXP-141: alpha_T(401 -> 503) = ln(N_T(503) / N_T(401)) / ln(503 / 401), N_T(503) from the EXP-141
   cells by step 3. In [1.0, 1.4] -> 'iso-time exponent constant (~1.2)'; > 1.4 -> 'rises with p'; < 1.0 -> 'falls'.
   T = 5000 primary; T = 3000 and 8000 reported as sensitivity.
Usage: python iso_time_s69.py [--seen-only]   (--seen-only: EXP-141 excluded, prints the prediction)
"""
import glob
import json
import math
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
SOURCES = ["EXP-137-modulus-density", "EXP-139-pair-count", "EXP-141-alpha-test"]
BUDGET = 30000


def cells(sources: list[str]) -> dict:
    out: dict = {}
    for src in sources:
        for f in glob.glob(os.path.join(ROOT, src, "raw", "*", "result.json")):
            r = json.load(open(f, encoding="utf-8"))
            if r.get("status") != "completed" or r.get("max_steps") != BUDGET or r.get("condition") != "baseline":
                continue
            p = r["config"]["p"]
            n = round(r["config"]["train_frac"] * p * p)
            g = ((r.get("transitions") or {}).get("primary", {}).get("generalization", {}) or {}).get(
                "first_crossing_step")
            out.setdefault((p, n), []).append(g)
    return out


def median(gs: list) -> float | None:
    if len(gs) < 6 or sum(g is not None for g in gs) < 4:
        return None
    v = sorted(math.inf if g is None else g for g in gs)
    return (v[2] + v[3]) / 2


def n_at(rows: list[tuple[int, float]], T: float, s: float) -> float:
    """rows: (N, median g) with defined medians, sorted by N."""
    if len(rows) >= 2:
        (n1, g1), (n2, g2) = sorted(rows, key=lambda r: abs(math.log(r[1] / T)))[:2]
        k = math.log(T / g1) / math.log(g2 / g1)
        return math.exp(math.log(n1) + k * (math.log(n2) - math.log(n1)))
    n1, g1 = rows[0]
    return n1 * (T / g1) ** (1 / s)


def main() -> None:
    seen_only = "--seen-only" in sys.argv
    c = cells(SOURCES[:2] if seen_only else SOURCES)
    med = {k: median(v) for k, v in c.items()}
    for k in sorted(c):
        print(k, "n_arms", len(c[k]), "gen", sorted(c[k], key=lambda g: (g is None, g or 0)), "median", med[k])
    by_p: dict = {}
    for (p, n), m in med.items():
        if m is not None:
            by_p.setdefault(p, []).append((n, m))
    slopes = []
    for p in (211, 307):
        (n1, g1), (n2, g2) = sorted(by_p[p])[:2]
        slopes.append(math.log(g2 / g1) / math.log(n2 / n1))
    s = sum(slopes) / len(slopes)
    print("local slopes", [round(x, 2) for x in slopes], "s", round(s, 2))
    for T in (5000, 3000, 8000):
        nt = {p: n_at(sorted(rows), T, s) for p, rows in sorted(by_p.items())}
        ps = [p for p in (211, 307, 401) if p in nt]
        xs = [math.log(p) for p in ps]
        ys = [math.log(nt[p]) for p in ps]
        xm, ym = sum(xs) / len(xs), sum(ys) / len(ys)
        a_fit = sum((x - xm) * (y - ym) for x, y in zip(xs, ys)) / sum((x - xm) ** 2 for x in xs)
        n503 = math.exp(ym + a_fit * (math.log(503) - xm))
        pred = {n: round(T * (n / n503) ** s) for n in (16100, 18100)}
        line = (f"T={T}: N_T {{{', '.join(f'{p}: {v:.0f}' for p, v in nt.items())}}}; alpha_T(211-401 fit) "
                f"{a_fit:.2f}; predicted N_T(503) {n503:.0f}; predicted median g {pred}")
        if 503 in nt and 401 in nt:
            a45 = math.log(nt[503] / nt[401]) / math.log(503 / 401)
            reading = ("iso-time exponent constant (~1.2)" if 1.0 <= a45 <= 1.4 else
                       "rises with p" if a45 > 1.4 else "falls")
            line += f"; observed alpha_T(401->503) {a45:.2f} -> {reading}"
        print(line)


if __name__ == "__main__":
    main()
