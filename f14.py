p='lab/tools/confirm_r14.py'
d=open(p,encoding='utf-8').read()
pairs=[
('''    steps = [int(x) for x in np.load(io.BytesIO(BLOCK.bound_bytes(man, d / "we_snapshot_steps.npy")))]
    gen = ((L.res.get("transitions") or {}).get("primary") or {}).get("generalization", {}).get("first_crossing_step")
''','''    steps = [int(x) for x in np.load(io.BytesIO(BLOCK.bound_bytes(man, d / "we_snapshot_steps.npy")))]
    gen = ((L.res.get("transitions") or {}).get("primary") or {}).get("generalization", {}).get("first_crossing_step")
    if (why := stop_mismatch(L.res.get("steps_completed"), gen, man)):     # pre-freeze review s67
        return f"defekt: {why}"
'''),
('''def run_info(man: dict, s: int, arm: str) -> dict | str:''','''def stop_mismatch(done: object, gen: object, man: dict) -> str | None:
    """steps_completed must follow the stop rule: all steps without generalization, else min(steps, gen + stop_after_gen)."""
    want = man["steps"] if gen is None else min(man["steps"], int(gen) + man["stop_after_gen"])
    return None if done == want else f"steps_completed {done!r} inconsistent with the stop rule (expected {want})"


def run_info(man: dict, s: int, arm: str) -> dict | str:'''),
('''    D = np.array([r["D"] for r in rows])''','''    ev_q = [r["q99"] for r in rows if r["evaluable"]]
    fail = -max(ev_q) if ev_q else -1.0                  # pre-freeze review s67: a non-generalizing seed counts like a seed at
    D = np.array([r["D"] if r["evaluable"] else fail for r in rows])   # placebo level with the largest observed q99, not milder'''),
('''Primary statistic per seed: D = Delta_pow - q99; a seed with an arm that never generalizes (or no snapshot >= g + 1000) enters as
D = -1 (counts against the claim; reported).''','''Primary statistic per seed: D = Delta_pow - q99; a seed with an arm that never generalizes (or no snapshot >= g + 1000) enters as
D = -max(q99 of the evaluable seeds) (-1 if none; counts against the claim like a seed at the largest placebo level; reported).
A run whose steps_completed does not follow the stop rule is a technical failure.'''),
('''    assert verdict(ok[:11] + [{"seed": 1, "technical": True}], rng)["verdict"] == "nicht auswertbar"''','''    assert verdict(ok[:11] + [{"seed": 1, "technical": True}], rng)["verdict"] == "nicht auswertbar"
    assert verdict(mixed, rng)["mean_D"] < (sum(r["D"] for r in ok[:6]) - 6 * 5.0) / 12 + 1e-9   # failures count as -max q99
    m = {"steps": 30000, "stop_after_gen": 2000}
    assert stop_mismatch(30000, None, m) is None and stop_mismatch(8125, 6125, m) is None and stop_mismatch(30000, 29000, m) is None
    assert stop_mismatch(8000, None, m) and stop_mismatch(30000, 6125, m)'''),
]
for a,b in pairs:
    assert d.count(a)==1,a[:50]; d=d.replace(a,b)
open(p,'w',encoding='utf-8',newline='\n').write(d)
p='lab/confirm/R14_REGISTRATION.md'
d=open(p,encoding='utf-8').read()
pairs=[
("nicht generalisierenden Arm (oder ohne Schnappschuss ≥ gen + 1000) geht mit **D = −1** ein (zählt gegen die Aussage, wird berichtet).",
 "nicht generalisierenden Arm (oder ohne Schnappschuss ≥ gen + 1000) geht mit **D = −(größtes q99 der auswertbaren Seeds)** ein (−1, falls keiner auswertbar; zählt wie ein Seed auf Placebo-Niveau, wird berichtet; nach der Prüfung vor dem Einfrieren strenger als die erste Fassung D = −1). Ein Lauf, dessen Schrittzahl nicht der Stoppregel folgt, ist ein technischer Ausfall."),
("in 6/6 Läufen Generalisierung und danach Δ_pow 8.2–10.9, jeweils über dem 99-%-Quantil eines Placebos.",
 "in 6/6 Läufen Generalisierung und danach Δ_pow 8.2–10.9, jeweils über dem 99-%-Quantil eines Placebos; bei p = 211 mit 10 % (4452 Paare) generalisierte dagegen keiner von 6 Läufen in 30 000 Schritten – „geringe Dichte“ heißt hier also ≈ 9425 Paare, nicht ein Anteil an sich."),
("Andere p/Anteile: nicht Teil von R14.",
 "Andere p/Anteile: nicht Teil von R14. Die Pilot-Splits stammen aus `EXP-043/make_split.py` (gleiche Wellen-/Schlüsselgewichtung, aber andere Zufallsströme und Zielziehung) – R14 nutzt die P1-Konstruktion."),
("`--splits`, `--jobs` → Dienst (gpu_gb 1.5, workers 6).",
 "`--splits`, `--jobs` → Dienst (gpu_gb 2.0 – im Pilot gemessen 1.7 GB max., workers 6, job_minutes 120)."),
]
for a,b in pairs:
    assert d.count(a)==1,a[:50]; d=d.replace(a,b)
open(p,'w',encoding='utf-8',newline='\n').write(d)
print('ok')
