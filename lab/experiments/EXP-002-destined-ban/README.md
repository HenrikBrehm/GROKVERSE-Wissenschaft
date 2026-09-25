# EXP-002: Verbot der „Ziel“-Frequenzen ab Schritt 1

**Status:** vorbereitet, **noch nicht ausgeführt**. Die Definition wurde am 2026-09-25 um
~17:00 Berlin fixiert (Sitzung 2), außerhalb des Run-Fensters. Der Code kommt aus EXP-001
(`freq_ban.py`, Bedingungen `ban_destined` und `ban_random --t0 1`) und ist ungetestet.
Spätere Kriterienänderungen gehören in EXP-002b.

## Warum

Die Studie (RESULTS §16.6, S3) zeigt, dass die Schlüsselfrequenzen vom Seed abhängen. Offen ist,
ob die Frequenzen, die ein Seed am Ende nutzt, **privilegiert** sind (zum Beispiel durch Init oder
Split früh festgelegt), oder ob das Netz ebenso gut beliebige andere Frequenzen nutzen kann.
EXP-003c legt nahe, dass sich die Spektralstruktur bei manchen Seeds früh vom Init-Niveau löst.
Ein Verbot ab Schritt 1 prüft, was es kostet, wenn der „vorgesehene“ Weg fehlt.

| | |
|---|---|
| **Fragestellung** | Verzögert ein Verbot der 5 Frequenzen, die der Seed ohne Eingriff am Ende nutzt, die Generalisierung stärker als ein Verbot von 5 beliebigen Frequenzen ab Schritt 1? |
| **Hypothese H-E2 (Nullhypothese als Arbeitsannahme)** | Nein: Die Zielfrequenzen sind nicht privilegiert, \|Δ(ban_destined) − Δ(ban_random_t1)\| < 500 Schritte |
| **Alternative** | Δ(ban_destined) − Δ(ban_random_t1) ≥ 1000 Schritte: Die Zielfrequenzen sind privilegiert |
| **Bedingungen** | `baseline` (= EXP-001-Baseline, wird wiederverwendet) · `ban_destined` (K = Top-5 des **gespeicherten** 25k-Modells desselben Seeds, ab Schritt 1) · `ban_random --t0 1` (K = 5 Frequenzen aus den Power-Rängen > 10 bei Schritt 1, Seed + 10007) |
| **Seeds** | 0, 1, 2 (Exploration, gleiche Seeds wie EXP-001) |
| **Messgrößen** | primär Δ = gen(Bedingung) − gen(baseline, gleicher Seed). Sekundär: finale Top-5 der gebannten Läufe · Überlapp mit den Rängen 6–10 des gespeicherten Finalmodells („Nachrücker“-Hypothese) · Frequenzzahl |
| **Validitätsprüfung** | Stimmen `final_top_m_freqs` der lokalen Baseline (4 Threads, torch 2.13) nicht mit den gespeicherten Top-5 überein, ist „destined“ für diesen Seed lokal nicht reproduziert. Der Seed wird dann gesondert berichtet und zählt nicht für die Entscheidung |
| **Entscheidungsregel** | *privilegiert*: Differenz ≥ 1000 in ≥ 2 von 3 gültigen Seeds (ein bei Cap zensierter `ban_destined`-Lauf bei nicht zensiertem Kontrolllauf zählt als ≥ 1000) · *nicht privilegiert*: \|Differenz\| < 500 in ≥ 2 von 3 · sonst *unklar*. Mit weniger als 2 gültigen Seeds ist das Ergebnis *nicht auswertbar* |
| **Budget** | Cap 15 000, Stopp 2000 Schritte nach dem Crossing, ≤ 20 min pro Lauf, 6 neue Läufe (die Baselines kommen aus EXP-001) |
| **Abbruch** | wie in EXP-001 (s/Schritt aus dem Funktionstest) |
| **Grenzen** | n = 3. Das Verbot greift nur an `W_E[:p]`. Andere Gewichte könnten die Frequenzen weiter tragen, zum Beispiel über W_pos oder die MLP. Das wäre selbst ein Befund und wird über die Spektren nur für W_E gemessen |

## Befehle (im Fenster, nach EXP-001)

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed S --condition ban_destined --out-root lab/experiments/EXP-002-destined-ban/raw
python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed S --condition ban_random --t0 1 --out-root lab/experiments/EXP-002-destined-ban/raw
```

Die Baselines liegen in `lab/experiments/EXP-001-freq-ban/raw/EXP-001_baseline_t2000_m5_seedS_thr4/`.
Ein Auswerteskript fehlt noch. Es soll nach dem Muster von `EXP-001-freq-ban/analyze.py` entstehen,
sobald die Ausgabe der EXP-001-Läufe real geprüft ist.
